from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContentReviewer(BaseTool):
    """
    Tool zur Überprüfung und Optimierung von Webseiten-Texten.
    Prüft auf Rechtschreibung, Grammatik, SEO und Lesbarkeit.
    """
    
    content: Dict = Field(
        ..., 
        description="Der zu überprüfende Content (meta und content)"
    )
    keywords: List[str] = Field(
        ..., 
        description="Die zu prüfenden Keywords"
    )
    style_guide: Dict = Field(
        ..., 
        description="Stilrichtlinien für die Überprüfung"
    )
    
    def run(self) -> Dict:
        """
        Führt eine umfassende Überprüfung des Contents durch
        """
        try:
            # Prompt für die Content-Überprüfung erstellen
            prompt = f"""
            Überprüfe den folgenden Content auf Qualität und Optimierungspotenzial:

            META-TITLE:
            {self.content.get('meta', {}).get('title', '')}

            META-DESCRIPTION:
            {self.content.get('meta', {}).get('description', '')}

            CONTENT:
            {self.content.get('content', '')}

            Zu prüfende Keywords: {', '.join(self.keywords)}
            
            Stilrichtlinien:
            - Tonalität: {self.style_guide.get('tonalitaet', 'professionell')}
            - Zielgruppe: {self.style_guide.get('zielgruppe', 'allgemein')}
            - Ansprache: {self.style_guide.get('ansprache', 'Sie')}

            Bitte analysiere:
            1. Meta-Informationen
               - Title-Tag (Länge, Keywords, Call-to-Action)
               - Meta-Description (Länge, Keywords, Anreiz zum Klicken)
            2. Content-Struktur
               - Überschriften-Hierarchie (H1, H2, etc.)
               - Absatzlängen und Lesbarkeit
               - Interne Verlinkung
            3. SEO-Optimierung
               - Keyword-Dichte und -Platzierung
               - LSI-Keywords und semantische Relevanz
               - Featured Snippet Potenzial
            4. Sprachqualität
               - Rechtschreibung und Grammatik
               - Stilistische Konsistenz
               - Tonalität und Zielgruppenansprache
            5. Conversion-Optimierung
               - Call-to-Actions (Platzierung und Formulierung)
               - Vertrauensbildende Elemente
               - User Journey und Lesefluss

            Formatiere die Antwort als JSON mit den folgenden Kategorien:
            - meta_analysis (Analyse der Meta-Informationen)
            - content_structure (Analyse der Content-Struktur)
            - seo_optimization (SEO-Analyse und Vorschläge)
            - language_quality (Sprachqualitätsanalyse)
            - conversion_optimization (CRO-Analyse)
            - improvement_suggestions (Konkrete Verbesserungsvorschläge)
            """
            
            # OpenAI API für die Analyse nutzen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Content-Editor und SEO-Experte. Führe eine gründliche Analyse durch und gib konkrete, umsetzbare Verbesserungsvorschläge. Formatiere die Ausgabe immer als korrektes JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Antwort verarbeiten
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "status": "success",
                "page_name": self.content.get('page_name', ''),
                "review": analysis
            }
            
        except Exception as e:
            print(f"Fehler bei der Content-Überprüfung: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    # Test mit dem generierten Content
    with open('content_generator_output.json', 'r') as f:
        generated_content = json.load(f)
    
    reviewer = ContentReviewer(
        content=generated_content,
        keywords=["Webdesign München", "Webdesign Agentur", "Website erstellen"],
        style_guide={
            "tonalitaet": "professionell und persönlich",
            "zielgruppe": "Kleine und mittlere Unternehmen in München",
            "ansprache": "Sie"
        }
    )
    result = reviewer.run()
    print(json.dumps(result, indent=2, ensure_ascii=False)) 