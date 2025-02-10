from agency_swarm import Agent
from agency_swarm.tools import BaseTool
from pydantic import Field, BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging

# Logging-Konfiguration
logger = logging.getLogger(__name__)

load_dotenv()

# OpenAI Client initialisieren
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContentParams(BaseModel):
    """Parameter für die Content-Generierung"""
    menu_item: str = Field(..., description="Der Name des Menüpunkts, für den Content generiert werden soll")
    num_paragraphs: int = Field(..., description="Anzahl der zu generierenden Absätze")
    words_per_paragraph: int = Field(..., description="Ungefähre Anzahl Wörter pro Absatz")
    briefing: str = Field(..., description="Das vollständige Briefing des Kunden")
    analysis: str = Field(..., description="Die finale Analyse des Briefings")

class ContentGeneratorTool(BaseTool):
    """
    Ein Tool zur Generierung von Website-Inhalten basierend auf dem Briefing und der Analyse.
    """
    params: ContentParams = Field(..., description="Parameter für die Content-Generierung")

    def run(self):
        """
        Generiert Inhalt für einen bestimmten Menüpunkt basierend auf den Parametern.
        """
        try:
            logger.debug(f"Content-Generierung gestartet für: {self.params.menu_item}")
            
            # Prompt für ChatGPT erstellen
            prompt = f"""
            Erstelle professionellen Website-Content für den Menüpunkt '{self.params.menu_item}' basierend auf dem folgenden Briefing und der Analyse.
            
            Briefing:
            {self.params.briefing}
            
            Analyse:
            {self.params.analysis}
            
            Anforderungen:
            - Erstelle genau {self.params.num_paragraphs} Absätze
            - Jeder Absatz soll ca. {self.params.words_per_paragraph} Wörter enthalten
            - Der Content muss perfekt auf die Zielgruppe und den Zweck der Website abgestimmt sein
            - Verwende einen professionellen, aber zugänglichen Schreibstil
            - Integriere wichtige Keywords und Themen aus dem Briefing
            - Strukturiere den Text mit passenden Zwischenüberschriften
            - Achte auf SEO-Optimierung und gute Lesbarkeit
            - Stelle sicher, dass der Content zur Gesamtstruktur der Website passt
            
            Formatierung:
            # [Menüpunkt: {self.params.menu_item}]
            [SEO-optimierte Hauptüberschrift]
            
            ## [Erste Zwischenüberschrift]
            [Erster Absatz]
            
            ## [Weitere Zwischenüberschriften]
            [Weitere Absätze]
            
            WICHTIG:
            1. Der Content muss sich perfekt in das Gesamtkonzept der Website einfügen
            2. Jeder Absatz muss einen klaren Mehrwert für den Leser bieten
            3. Die Überschriften müssen SEO-optimiert und ansprechend sein
            4. Der Text muss die Zielgruppe direkt ansprechen und überzeugen
            5. Berücksichtige alle Informationen aus dem Briefing und der Analyse"""
            
            # OpenAI API für die Generierung nutzen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": """Du bist ein erfahrener Website-Texter und Content-Stratege.
                    - Du erstellst hochwertige, SEO-optimierte Texte
                    - Du achtest besonders auf Zielgruppenansprache und Conversion
                    - Du verstehst es, komplexe Themen verständlich zu vermitteln
                    - Du kreierst überzeugende Überschriften und Textstrukturen"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generierter Content: {content[:100]}...")
            return content
            
        except Exception as e:
            error_msg = f"Fehler bei der Inhaltsgenerierung: {str(e)}"
            logger.error(error_msg)
            return error_msg

def create_content(menu_item: str, num_paragraphs: int, words_per_paragraph: int, briefing: str, analysis: str) -> str:
    """
    Hilfsfunktion zur Erstellung von Inhalten
    """
    try:
        logger.debug(f"Erstelle Content für Menüpunkt: {menu_item}")
        params = ContentParams(
            menu_item=menu_item,
            num_paragraphs=num_paragraphs,
            words_per_paragraph=words_per_paragraph,
            briefing=briefing,
            analysis=analysis
        )
        
        tool = ContentGeneratorTool(params=params)
        return tool.run()
    except Exception as e:
        error_msg = f"Fehler: {str(e)}"
        logger.error(error_msg)
        return error_msg

class ContentCreationAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ContentCreationAgent",
            description="Ein Agent für die Erstellung von Website-Content",
            instructions="./instructions.md",
            tools=[ContentGeneratorTool]
        )
    
    def create_content(self, briefing_data):
        """Erstellt Website-Content basierend auf dem Briefing"""
        try:
            content_params = briefing_data.get('content_params', {})
            tool = ContentGeneratorTool(
                params=ContentParams(
                    menu_item=content_params.get('menu_item', ''),
                    num_paragraphs=content_params.get('num_paragraphs', 3),
                    words_per_paragraph=content_params.get('words_per_paragraph', 150),
                    briefing=briefing_data.get('original_briefing', ''),
                    analysis=briefing_data.get('final_analysis', '')
                )
            )
            return tool.run()
        except Exception as e:
            return f"Fehler bei der Content-Erstellung: {str(e)}" 