from agency_swarm import Agent
from agency_swarm.tools import BaseTool
from pydantic import Field
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Client initialisieren
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AnalyzeBriefingTool(BaseTool):
    """Analysiert ein Website-Briefing und erstellt eine strukturierte Analyse."""
    
    briefing: str = Field(..., description="Das zu analysierende Website-Briefing")
    
    def extract_menu_items(self, analysis):
        """Extrahiert die Menüpunkte aus der Analyse"""
        try:
            # Finde den Seitenstruktur-Abschnitt
            structure_start = analysis.find("📑 Seitenstruktur")
            if structure_start == -1:
                structure_start = analysis.lower().find("seitenstruktur")
            
            structure_end = analysis.find("🎯 Zielgruppen-Analyse")
            if structure_end == -1:
                structure_end = analysis.lower().find("zielgruppen")
                if structure_end == -1:
                    structure_end = len(analysis)
            
            if structure_start != -1:
                structure_text = analysis[structure_start:structure_end].strip()
                
                # Extrahiere die Menüpunkte (Zeilen die mit - oder • beginnen)
                menu_items = [line.strip('- •').split(':')[0].strip() 
                             for line in structure_text.split('\n') 
                             if line.strip().startswith(('-', '•'))]
                
                # Wenn keine Menüpunkte gefunden wurden, füge Standardmenüpunkte hinzu
                if not menu_items:
                    menu_items = ["Startseite", "Über uns", "Leistungen", "Kontakt"]
                
                return menu_items
            
            return ["Startseite", "Über uns", "Leistungen", "Kontakt"]
            
        except Exception as e:
            return ["Startseite", "Über uns", "Leistungen", "Kontakt"]
    
    def run(self):
        try:
            # Erstelle den Prompt für ChatGPT
            prompt = f"""Analysiere das folgende Website-Briefing und erstelle eine strukturierte Analyse.
            Berücksichtige dabei die folgenden Aspekte:
            - Projektziele und Hauptanforderungen
            - Zielgruppen-Analyse
            - Gewünschte Seitenstruktur (WICHTIG: Liste ALLE Menüpunkte mit Beschreibung auf)
            - Besondere Anforderungen oder Wünsche

            Briefing:
            {self.briefing}

            Formatiere die Analyse EXAKT wie folgt:
            📋 Projektziele
            ============
            - Ziel 1
            - Ziel 2
            ...

            📑 Seitenstruktur
            ==============
            - Homepage: Kurze Beschreibung der Startseite und ihrer Hauptelemente
            - Über Uns: Vorstellung des Unternehmens, Team, Geschichte
            - Leistungen: Detaillierte Beschreibung der angebotenen Dienstleistungen
            - Kontakt: Kontaktformular, Adresse, Anfahrt
            [Füge hier ALLE weiteren Menüpunkte hinzu, die im Briefing erwähnt werden]

            🎯 Zielgruppen-Analyse
            ==================
            - Zielgruppe 1
            - Zielgruppe 2
            ...

            ⭐ Besondere Anforderungen
            =====================
            - Anforderung 1
            - Anforderung 2
            ...

            WICHTIG: 
            1. Stelle sicher, dass ALLE im Briefing erwähnten oder implizit benötigten Menüpunkte unter "Seitenstruktur" aufgelistet sind
            2. Jeder Menüpunkt MUSS mit einem Bindestrich beginnen und eine kurze Beschreibung nach dem Doppelpunkt haben
            3. Die Standardmenüpunkte (Homepage, Über Uns, Leistungen, Kontakt) MÜSSEN immer enthalten sein, außer es wird explizit anders gewünscht"""

            # ChatGPT API aufrufen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Verwende GPT-4 für bessere Analyse
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Website-Analyst, der Briefings analysiert und strukturiert aufbereitet. Achte besonders darauf, ALLE relevanten Menüpunkte zu identifizieren und im korrekten Format aufzulisten."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extrahiere die Analyse aus der Antwort
            analysis = response.choices[0].message.content
            
            # Extrahiere die Menüpunkte direkt hier
            menu_items = self.extract_menu_items(analysis)
            
            # Gib beides als Dictionary zurück
            return {
                "analysis": analysis,
                "menu_items": menu_items
            }
            
        except Exception as e:
            return {
                "analysis": f"Fehler bei der Analyse: {str(e)}",
                "menu_items": ["Startseite", "Über uns", "Leistungen", "Kontakt"]
            }

class SEOResearchTool(BaseTool):
    """Schlägt SEO-relevante Begriffe basierend auf dem Briefing vor."""
    
    briefing: str = Field(..., description="Das Briefing für die SEO-Analyse")
    
    def run(self):
        try:
            # Erstelle den Prompt für ChatGPT
            prompt = f"""Analysiere das folgende Website-Briefing und schlage relevante SEO-Begriffe vor.
            Berücksichtige dabei die folgenden Kategorien:
            - Hauptkeywords (Die wichtigsten Suchbegriffe für die Branche)
            - Themencluster (Verwandte Themenbereiche und Begriffsgruppen)
            - Longtail-Keywords (Spezifische Suchphrasen und Nischen-Keywords)
            - Lokale SEO (Standortbezogene und regionale Suchbegriffe)

            Briefing:
            {self.briefing}

            Formatiere die Analyse wie folgt:
            🎯 Hauptkeywords
            =============
            - Keyword 1
            - Keyword 2
            ...

            📊 Themencluster
            =============
            - Cluster 1
            - Cluster 2
            ...

            💡 Longtail-Keywords
            ================
            - Phrase 1
            - Phrase 2
            ...

            🔍 Lokale SEO
            ==========
            - Begriff 1
            - Begriff 2
            ..."""

            # ChatGPT API aufrufen
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener SEO-Experte, der Websites analysiert und relevante Keywords vorschlägt."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extrahiere die SEO-Analyse aus der Antwort
            seo_analysis = response.choices[0].message.content
            
            return seo_analysis
            
        except Exception as e:
            return f"Fehler bei der SEO-Analyse: {str(e)}"

class QuestionGeneratorTool(BaseTool):
    """Generiert Verständnisfragen basierend auf dem Briefing."""
    
    briefing: str = Field(..., description="Das Briefing, zu dem Fragen generiert werden sollen")
    
    def run(self):
        try:
            # Erstelle den Prompt für ChatGPT
            prompt = f"""Analysiere das folgende Website-Briefing und generiere wichtige Verständnisfragen.
            Die Fragen sollten helfen, das Briefing zu präzisieren und fehlende Informationen zu identifizieren.

            Briefing:
            {self.briefing}

            Formatiere die Fragen wie folgt:
            1. Frage 1?
            2. Frage 2?
            ..."""

            # ChatGPT API aufrufen
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Website-Analyst, der wichtige Verständnisfragen generiert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extrahiere die Fragen aus der Antwort
            questions = response.choices[0].message.content
            
            return questions
            
        except Exception as e:
            return f"Fehler bei der Fragen-Generierung: {str(e)}"

class UpdateAnalysisTool(BaseTool):
    """Aktualisiert die Analyse basierend auf den Antworten."""
    
    initial_briefing: str = Field(..., description="Das ursprüngliche Briefing")
    questions: str = Field(..., description="Die gestellten Fragen")
    answers: str = Field(..., description="Die Antworten auf die Fragen")
    
    def extract_menu_items(self, analysis):
        """Extrahiert die Menüpunkte aus der Analyse"""
        try:
            # Finde den Seitenstruktur-Abschnitt
            structure_start = analysis.find("📑 Seitenstruktur")
            if structure_start == -1:
                structure_start = analysis.lower().find("seitenstruktur")
            
            structure_end = analysis.find("🎯 Zielgruppen-Analyse")
            if structure_end == -1:
                structure_end = analysis.lower().find("zielgruppen")
                if structure_end == -1:
                    structure_end = len(analysis)
            
            if structure_start != -1:
                structure_text = analysis[structure_start:structure_end].strip()
                
                # Extrahiere die Menüpunkte (Zeilen die mit - oder • beginnen)
                menu_items = [line.strip('- •').split(':')[0].strip() 
                             for line in structure_text.split('\n') 
                             if line.strip().startswith(('-', '•'))]
                
                # Wenn keine Menüpunkte gefunden wurden, füge Standardmenüpunkte hinzu
                if not menu_items:
                    menu_items = ["Startseite", "Über uns", "Leistungen", "Kontakt"]
                
                return menu_items
            
            return ["Startseite", "Über uns", "Leistungen", "Kontakt"]
            
        except Exception as e:
            return ["Startseite", "Über uns", "Leistungen", "Kontakt"]
    
    def run(self):
        try:
            # Erstelle den Prompt für ChatGPT
            prompt = f"""Aktualisiere die Website-Analyse basierend auf den neuen Informationen.

            Ursprüngliches Briefing:
            {self.initial_briefing}

            Gestellte Fragen:
            {self.questions}

            Erhaltene Antworten:
            {self.answers}

            Erstelle eine aktualisierte, vollständige Analyse EXAKT im folgenden Format:
            📋 Projektziele
            ============
            - Ziel 1
            - Ziel 2
            ...

            📑 Seitenstruktur
            ==============
            - Homepage: Kurze Beschreibung der Startseite und ihrer Hauptelemente
            - Über Uns: Vorstellung des Unternehmens, Team, Geschichte
            - Leistungen: Detaillierte Beschreibung der angebotenen Dienstleistungen
            - Kontakt: Kontaktformular, Adresse, Anfahrt
            [Füge hier ALLE weiteren Menüpunkte hinzu, die im Briefing oder den Antworten erwähnt werden]

            🎯 Zielgruppen-Analyse
            ==================
            - Zielgruppe 1
            - Zielgruppe 2
            ...

            ⭐ Besondere Anforderungen
            =====================
            - Anforderung 1
            - Anforderung 2
            ...

            WICHTIG: 
            1. Stelle sicher, dass ALLE im Briefing und in den Antworten erwähnten oder implizit benötigten Menüpunkte unter "Seitenstruktur" aufgelistet sind
            2. Jeder Menüpunkt MUSS mit einem Bindestrich beginnen und eine kurze Beschreibung nach dem Doppelpunkt haben
            3. Die Standardmenüpunkte (Homepage, Über Uns, Leistungen, Kontakt) MÜSSEN immer enthalten sein, außer es wird explizit anders gewünscht"""

            # ChatGPT API aufrufen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Website-Analyst, der Analysen basierend auf neuen Informationen aktualisiert. Achte besonders darauf, ALLE relevanten Menüpunkte zu identifizieren und im korrekten Format aufzulisten."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extrahiere die aktualisierte Analyse aus der Antwort
            updated_analysis = response.choices[0].message.content
            
            # Extrahiere die Menüpunkte direkt hier
            menu_items = self.extract_menu_items(updated_analysis)
            
            # Gib beides als Dictionary zurück
            return {
                "analysis": updated_analysis,
                "menu_items": menu_items
            }
            
        except Exception as e:
            return {
                "analysis": f"Fehler bei der Aktualisierung: {str(e)}",
                "menu_items": ["Startseite", "Über uns", "Leistungen", "Kontakt"]
            }

class WebdesignAgent(Agent):
    def __init__(self):
        super().__init__(
            name="WebdesignAgent",
            description="Ein Agent für die Analyse von Website-Briefings und SEO-Optimierung",
            instructions="./instructions.md",
            tools=[AnalyzeBriefingTool, SEOResearchTool, QuestionGeneratorTool, UpdateAnalysisTool]
        )
    
    def analyze_briefing(self, briefing):
        """Analysiert ein Website-Briefing"""
        tool = AnalyzeBriefingTool(briefing=briefing)
        return tool.run()
    
    def suggest_seo_terms(self, briefing):
        """Schlägt SEO-relevante Begriffe vor"""
        tool = SEOResearchTool(briefing=briefing)
        return tool.run()
    
    def generate_questions(self, briefing):
        """Generiert Verständnisfragen zum Briefing"""
        tool = QuestionGeneratorTool(briefing=briefing)
        return tool.run()
    
    def update_analysis(self, initial_briefing, questions, answers):
        """Aktualisiert die Analyse basierend auf den Antworten"""
        tool = UpdateAnalysisTool(
            initial_briefing=initial_briefing,
            questions=questions,
            answers=answers
        )
        return tool.run() 