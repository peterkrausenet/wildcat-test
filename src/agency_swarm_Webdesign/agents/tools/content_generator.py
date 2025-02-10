from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContentGenerator(BaseTool):
    """
    Ein Tool zur dynamischen Content-Generierung basierend auf Briefing-Analyse.
    """
    
    briefing: str = Field(
        ..., description="Das vollständige Briefing des Benutzers"
    )
    
    keywords: str = Field(
        default="", description="Kommagetrennte Keywords"
    )
    
    target_audience: str = Field(
        default="", description="Die Zielgruppe für den Content"
    )
    
    tone: str = Field(
        default="", description="Gewünschte Tonalität des Textes"
    )
    
    words_per_section: int = Field(
        default=150, description="Ungefähre Wortanzahl pro Abschnitt"
    )

    def _analyze_briefing(self):
        """
        Analysiert das Briefing und extrahiert wichtige Informationen.
        """
        briefing_info = {
            "sections": self._extract_sections(),
            "key_points": self._extract_key_points(),
            "tone": self._extract_tone(),
            "target_group": self._extract_target_group(),
            "unique_features": self._extract_unique_features(),
            "call_to_actions": self._extract_ctas()
        }
        
        # Prüfe auf fehlende wichtige Informationen
        missing_info = []
        if not briefing_info["sections"]:
            missing_info.append("Welche Sektionen/Abschnitte soll der Text enthalten?")
        if not briefing_info["key_points"]:
            missing_info.append("Was sind die wichtigsten Botschaften, die vermittelt werden sollen?")
        if not briefing_info["target_group"] and not self.target_audience:
            missing_info.append("Für welche Zielgruppe soll der Text geschrieben werden?")
            
        return briefing_info, missing_info

    def _extract_sections(self):
        """Extrahiert die gewünschten Sektionen aus dem Briefing."""
        sections = []
        lines = self.briefing.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
                
            # Suche nach Sektionsmarkierungen
            if any(marker in line for marker in ["abschnitt:", "sektion:", "kapitel:", "teil:"]):
                if current_section:
                    sections.append(current_section)
                current_section = {"title": line.split(":", 1)[1].strip(), "content": []}
            elif current_section:
                current_section["content"].append(line)
            elif ":" in line and not any(url_marker in line.lower() for url_marker in ["http", "www", "https"]):
                sections.append({"title": line.split(":", 1)[0].strip(), "content": [line.split(":", 1)[1].strip()]})
        
        if current_section:
            sections.append(current_section)
            
        return sections

    def _extract_key_points(self):
        """Extrahiert die Kernbotschaften aus dem Briefing."""
        key_points = []
        lines = self.briefing.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Suche nach Aufzählungen und wichtigen Punkten
            if line.startswith(("-", "•", "*", "→", ">")):
                key_points.append(line[1:].strip())
            elif ":" in line and len(line.split(":")[1].strip()) > 10:
                key_points.append(line.split(":")[1].strip())
                
        return key_points

    def _extract_tone(self):
        """Extrahiert den gewünschten Tonfall aus dem Briefing."""
        if self.tone:
            return self.tone
            
        tone_indicators = {
            "professionell": ["professionell", "seriös", "geschäftlich", "business"],
            "freundlich": ["freundlich", "warm", "persönlich", "familiär"],
            "informativ": ["informativ", "sachlich", "fachlich", "detailliert"],
            "motivierend": ["motivierend", "inspirierend", "begeisternd"],
            "locker": ["locker", "casual", "entspannt", "ungezwungen"]
        }
        
        briefing_lower = self.briefing.lower()
        detected_tones = []
        
        for tone, indicators in tone_indicators.items():
            if any(indicator in briefing_lower for indicator in indicators):
                detected_tones.append(tone)
                
        return detected_tones[0] if detected_tones else "professionell"

    def _extract_target_group(self):
        """Extrahiert die Zielgruppe aus dem Briefing."""
        if self.target_audience:
            return self.target_audience
            
        target_group_patterns = [
            r"zielgruppe[:\s]+([^\.]+)",
            r"(?:richtet sich an|für)[:\s]+([^\.]+)",
            r"(?:kunden|kundenkreis)[:\s]+([^\.]+)"
        ]
        
        briefing_lower = self.briefing.lower()
        
        for pattern in target_group_patterns:
            match = re.search(pattern, briefing_lower)
            if match:
                return match.group(1).strip()
                
        return None

    def _extract_unique_features(self):
        """Extrahiert Alleinstellungsmerkmale aus dem Briefing."""
        features = []
        feature_markers = [
            "besonderheit", "vorteil", "unique", "alleinstellungsmerkmal",
            "unterschied", "stärke", "speziell", "besonders"
        ]
        
        lines = self.briefing.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            if any(marker in line for marker in feature_markers):
                if ":" in line:
                    features.append(line.split(":", 1)[1].strip())
                else:
                    features.append(line)
                    
        return features

    def _extract_ctas(self):
        """Extrahiert gewünschte Call-to-Actions aus dem Briefing."""
        ctas = []
        cta_markers = [
            "call to action", "cta", "handlungsaufforderung",
            "kontakt", "anfrage", "termin"
        ]
        
        lines = self.briefing.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            if any(marker in line for marker in cta_markers):
                if ":" in line:
                    ctas.append(line.split(":", 1)[1].strip())
                else:
                    ctas.append(line)
                    
        return ctas

    def _create_generation_prompt(self, briefing_info):
        """Erstellt einen strukturierten Prompt für die Content-Generierung."""
        prompt_parts = []
        
        # Aufgabenbeschreibung
        prompt_parts.append("Erstelle einen überzeugenden Text mit folgenden Vorgaben:")
        
        # Sektionen
        if briefing_info["sections"]:
            prompt_parts.append("\nGewünschte Sektionen:")
            for section in briefing_info["sections"]:
                prompt_parts.append(f"- {section['title']}")
                if section['content']:
                    prompt_parts.append(f"  Details: {' '.join(section['content'])}")
        
        # Kernbotschaften
        if briefing_info["key_points"]:
            prompt_parts.append("\nKernbotschaften:")
            for point in briefing_info["key_points"]:
                prompt_parts.append(f"- {point}")
        
        # Zielgruppe
        target_group = briefing_info["target_group"] or self.target_audience
        if target_group:
            prompt_parts.append(f"\nZielgruppe: {target_group}")
        
        # Tonalität
        tone = briefing_info["tone"] or self.tone
        if tone:
            prompt_parts.append(f"\nTonalität: {tone}")
        
        # Alleinstellungsmerkmale
        if briefing_info["unique_features"]:
            prompt_parts.append("\nAlleinstellungsmerkmale:")
            for feature in briefing_info["unique_features"]:
                prompt_parts.append(f"- {feature}")
        
        # Call-to-Actions
        if briefing_info["call_to_actions"]:
            prompt_parts.append("\nGewünschte Call-to-Actions:")
            for cta in briefing_info["call_to_actions"]:
                prompt_parts.append(f"- {cta}")
        
        # Keywords
        if self.keywords:
            prompt_parts.append(f"\nZu integrierende Keywords: {self.keywords}")
        
        # Spezifische Anweisungen
        prompt_parts.append("\nBitte beachte:")
        prompt_parts.append("- Erstelle einen natürlich fließenden Text")
        prompt_parts.append("- Integriere die Keywords organisch")
        prompt_parts.append("- Halte die Tonalität konsistent")
        prompt_parts.append("- Füge passende Überschriften ein")
        prompt_parts.append("- Verwende maximal 150 Wörter pro Absatz")
        
        return "\n".join(prompt_parts)

    def run(self):
        """
        Führt die Content-Generierung durch.
        """
        try:
            # Analysiere das Briefing
            briefing_info, missing_info = self._analyze_briefing()
            
            # Wenn wichtige Informationen fehlen, gib Fragen zurück
            if missing_info:
                return json.dumps({
                    "status": "needs_clarification",
                    "questions": missing_info
                })
            
            # Erstelle den Generierungs-Prompt
            prompt = self._create_generation_prompt(briefing_info)
            
            # OpenAI API für die Generierung nutzen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein professioneller Content-Creator mit Fokus auf SEO-optimierte Webtexte."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Antwort verarbeiten
            generated_content = response.choices[0].message.content
            
            return json.dumps({
                "status": "success",
                "content": generated_content,
                "debug_info": {
                    "analyzed_briefing": briefing_info,
                    "generation_prompt": prompt
                }
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })

if __name__ == "__main__":
    # Test
    generator = ContentGenerator(
        briefing="""
        Abschnitt: Einleitung
        Eine kurze Vorstellung unserer Webdesign-Agentur.
        
        Abschnitt: Leistungen
        - Responsive Webdesign
        - SEO-Optimierung
        - Content-Erstellung
        
        Zielgruppe: Kleine und mittlere Unternehmen in München
        Tonalität: Professionell und persönlich
        
        Besonderheiten:
        - 10 Jahre Erfahrung
        - Persönliche Betreuung
        - Faire Preise
        """,
        keywords="Webdesign München, SEO-Optimierung, Responsive Design",
        target_audience="KMUs in München",
        tone="professionell"
    )
    
    result = generator.run()
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False)) 