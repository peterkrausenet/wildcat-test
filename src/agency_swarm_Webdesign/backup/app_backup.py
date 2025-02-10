import os
import sys
import gradio as gr
import json
import re
import logging
from datetime import datetime
from dotenv import load_dotenv

# Konfiguriere Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Lade die Umgebungsvariablen
load_dotenv()
logger.info("Umgebungsvariablen geladen")

# Füge den Projektpfad zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
logger.info(f"Projektpfad hinzugefügt: {project_root}")

try:
    from content_creation_agent.tools.seo_researcher import SEOResearcher
    from content_creation_agent.tools.content_generator import ContentGenerator
    from content_creation_agent.tools.content_reviewer import ContentReviewer
    logger.info("Alle Tools erfolgreich importiert")
except Exception as e:
    logger.error(f"Fehler beim Importieren der Tools: {str(e)}")
    raise

# Globaler Speicher für das finale Briefing
complete_briefing = {}

def analyze_briefing(briefing):
    """Analysiert das Briefing und generiert relevante Verständnisfragen"""
    logger.info("Starte Briefing-Analyse")
    try:
        content_generator = ContentGenerator()
        prompt = f"""Generiere gezielte Verständnisfragen zum folgenden Briefing:
        {briefing}
        
        Konzentriere dich dabei auf:
        - Fehlende wichtige Informationen
        - Unklare oder mehrdeutige Aussagen
        - Lücken in den Kernbotschaften
        - Fehlende Details zum Unternehmen oder den Dienstleistungen
        - Unklare Alleinstellungsmerkmale (USPs)
        
        Formuliere 3-4 präzise Fragen, die für die Content-Erstellung essentiell sind.
        Gib NUR die Fragen zurück, keine Analyse oder Zusammenfassung."""
        
        logger.debug(f"Sende Prompt an ContentGenerator: {prompt[:100]}...")
        questions = content_generator.generate(prompt)
        logger.info("Fragen erfolgreich generiert")
        return questions if questions else "Keine offenen Fragen identifiziert."
    except Exception as e:
        logger.error(f"Fehler bei der Briefing-Analyse: {str(e)}")
        return f"Fehler bei der Analyse: {str(e)}"

def start_briefing_analysis(briefing):
    """Startet die Briefing-Analyse mit interaktivem Chat"""
    logger.info("Starte vollständige Briefing-Analyse")
    
    if not briefing or not briefing.strip():
        error_msg = "Bitte gib ein Briefing ein."
        logger.error(error_msg)
        return error_msg
    
    try:
        logger.debug(f"Initialisiere Content Generator und SEO Researcher")
        content_generator = ContentGenerator()
        seo_researcher = SEOResearcher()
        
        logger.debug(f"Starte Content-Analyse mit Briefing: {briefing[:100]}...")
        content_analysis = content_generator.generate(briefing)
        if not content_analysis:
            raise ValueError("Keine Content-Analyse generiert")
        logger.debug(f"Content-Analyse Ergebnis: {content_analysis[:100]}...")
        
        logger.debug("Starte SEO-Analyse")
        seo_terms = seo_researcher.suggest_industry_terms(briefing)
        if not seo_terms:
            logger.warning("Keine SEO-Begriffe gefunden")
            seo_terms = "Keine spezifischen SEO-Begriffe identifiziert."
        logger.debug(f"SEO-Begriffe: {seo_terms[:100]}...")
        
        logger.debug("Generiere Verständnisfragen")
        questions = analyze_briefing(briefing)
        if not questions:
            logger.warning("Keine Fragen generiert")
            questions = "Keine spezifischen Rückfragen notwendig."
        logger.debug(f"Generierte Fragen: {questions[:100]}...")
        
        analysis_result = f"""📋 Briefing-Analyse
=================

{content_analysis}

🎯 SEO-Optimierung
================
{seo_terms}

❓ Rückfragen zur Klärung
======================
{questions}

Bitte überprüfe die Analyse und beantworte die Rückfragen, damit wir den Content optimal auf deine Bedürfnisse abstimmen können."""

        logger.info("Briefing-Analyse erfolgreich abgeschlossen")
        logger.debug(f"Vollständiges Analyse-Ergebnis: {analysis_result[:200]}...")
        return analysis_result
    except Exception as e:
        error_msg = f"Fehler bei der Briefing-Analyse: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"""⚠️ Fehler bei der Analyse

Es ist ein Fehler aufgetreten: {str(e)}

Bitte versuche es erneut oder kontaktiere den Support, wenn der Fehler bestehen bleibt.
Debug-Information für den Support: {type(e).__name__}"""

def process_answers(initial_briefing, questions, answers):
    """Verarbeitet die Antworten und aktualisiert die Analyse"""
    logger.info("Verarbeite Antworten")
    
    if not answers or not answers.strip():
        error_msg = "Bitte gib deine Antworten ein."
        logger.error(error_msg)
        return error_msg
    
    try:
        # Aktualisiere die Analyse mit den Antworten
        updated_analysis = update_complete_briefing(initial_briefing, questions, answers)
        if not updated_analysis:
            raise ValueError("Keine aktualisierte Analyse generiert")
        
        result = f"""📋 Aktualisierte Briefing-Analyse
==========================

{updated_analysis}

✅ Die Analyse wurde gespeichert und wird als Grundlage für die Content-Erstellung verwendet."""
        
        logger.info("Antworten erfolgreich verarbeitet")
        return result
    except Exception as e:
        error_msg = f"Fehler bei der Verarbeitung der Antworten: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"""⚠️ Fehler bei der Verarbeitung

Es ist ein Fehler aufgetreten: {str(e)}

Bitte versuche es erneut oder kontaktiere den Support, wenn der Fehler bestehen bleibt.
Debug-Information für den Support: {type(e).__name__}"""

def show_stored_briefing():
    """Zeigt das gespeicherte Briefing an"""
    global complete_briefing
    if not complete_briefing:
        return "Noch kein Briefing gespeichert."
    
    return f"""📋 Gespeichertes Briefing
==================

🎯 Grundinformationen
------------------
Branche: {complete_briefing.get('industry', 'Nicht definiert')}
Tonalität: {complete_briefing.get('tone', 'Nicht definiert')}

💡 Kernbotschaften
---------------
{complete_briefing.get('key_messages', 'Keine Kernbotschaften definiert')}

🔍 SEO-Keywords
------------
{complete_briefing.get('seo_terms', 'Keine SEO-Terms definiert')}

📝 Ursprüngliches Briefing
----------------------
{complete_briefing.get('original_briefing', 'Kein ursprüngliches Briefing vorhanden')}

❓ Klärungen
---------
Fragen: 
{complete_briefing.get('questions_and_answers', {}).get('questions', 'Keine Fragen gestellt')}

Antworten:
{complete_briefing.get('questions_and_answers', {}).get('answers', 'Keine Antworten vorhanden')}

📊 Konsolidierte Analyse
--------------------
{complete_briefing.get('consolidated_analysis', 'Keine konsolidierte Analyse vorhanden')}

⏰ Letzte Aktualisierung: {complete_briefing.get('timestamp', 'Unbekannt')}"""

def extract_menu_items(briefing):
    """Extrahiert die Menüpunkte/Seiten aus dem Briefing"""
    content_generator = ContentGenerator()
    
    prompt = f"""Analysiere das folgende Briefing und extrahiere alle gewünschten Menüpunkte/Seiten der Website:
    {briefing}
    
    Gib nur die Menüpunkte als kommagetrennte Liste zurück.
    Standardmenüpunkte (Startseite, Über uns, Kontakt) hinzufügen, falls nicht explizit anders gewünscht."""
    
    menu_items = content_generator.generate(prompt)
    # Säubere und formatiere die Ausgabe
    items = [item.strip() for item in menu_items.split(',')]
    return items if items else ["Startseite", "Über uns", "Leistungen", "Kontakt"]

def extract_company_facts(briefing):
    """Extrahiert wichtige Unternehmensfakten aus dem Briefing"""
    content_generator = ContentGenerator()
    
    prompt = f"""Extrahiere NUR die wichtigsten Fakten über das Unternehmen aus dem folgenden Text.
    Ignoriere dabei alle anderen Informationen wie Standort, SEO-Keywords etc.
    
    Text:
    {briefing}
    
    Berücksichtige ausschließlich:
    - Name und Art des Unternehmens
    - Gründungsjahr/Geschichte
    - Kernkompetenzen und Hauptprodukte/Dienstleistungen
    - Teamgröße/Mitarbeiteranzahl
    - Auszeichnungen/Zertifizierungen
    
    Formatiere die Fakten als kurze, prägnante Aufzählung.
    Nenne NUR die tatsächlich im Text erwähnten Fakten."""
    
    facts = content_generator.generate(prompt)
    return facts if facts else "Keine Unternehmensfakten gefunden."

def extract_location_info(briefing):
    """Extrahiert Standortinformationen aus dem Briefing"""
    content_generator = ContentGenerator()
    
    prompt = f"""Extrahiere NUR die standortbezogenen Informationen aus dem folgenden Text.
    Ignoriere dabei alle anderen Informationen wie Unternehmensfakten, SEO-Keywords etc.
    
    Text:
    {briefing}
    
    Berücksichtige ausschließlich:
    - Hauptstandort/Adresse
    - Geschäftsgebiet/Einzugsbereich
    - Erreichbarkeit/Verkehrsanbindung
    - Besondere Lagemerkmale
    
    Formatiere die Informationen als kurze, prägnante Aufzählung.
    Nenne NUR die tatsächlich im Text erwähnten Standortinformationen."""
    
    location = content_generator.generate(prompt)
    return location if location else "Keine Standortinformationen gefunden."

def get_briefing_info():
    """Holt alle relevanten Informationen aus dem gespeicherten Briefing"""
    global complete_briefing
    if not complete_briefing:
        return {
            'menu_items': [],
            'industry': "Nicht definiert",
            'company_facts': "Keine Unternehmensfakten verfügbar",
            'location_info': "Keine Standortinformationen verfügbar"
        }
    
    # Extrahiere Menüpunkte aus dem ursprünglichen Briefing
    menu_items = extract_menu_items(complete_briefing.get('original_briefing', ''))
    
    # Verwende die konsolidierte Analyse für Unternehmensfakten und Standortinformationen
    consolidated_analysis = complete_briefing.get('consolidated_analysis', '')
    company_facts = extract_company_facts(consolidated_analysis)
    location_info = extract_location_info(consolidated_analysis)
    
    return {
        'menu_items': menu_items,
        'industry': complete_briefing.get('industry', 'Nicht definiert'),
        'company_facts': company_facts,
        'location_info': location_info
    }

def switch_to_content_tab():
    """Wechselt zum Content-Erstellungs-Tab"""
    logger.info("Wechsle zum Content-Erstellungs-Tab")
    try:
        return {"selected": "content_tab"}
    except Exception as e:
        error_msg = f"Fehler beim Tab-Wechsel: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"selected": "briefing_tab"}  # Fallback zum Briefing-Tab

# Hilfsfunktionen für die UI
def toggle_edit(textbox):
    """Schaltet die Bearbeitbarkeit eines Textfeldes um"""
    return {"interactive": not textbox.interactive}

def add_menu_item_handler(new_item, current_items):
    """Fügt einen neuen Menüpunkt hinzu"""
    if new_item and new_item not in current_items.choices:
        updated_items = current_items.choices + [new_item]
        return [
            {"choices": updated_items},  # Dropdown update
            {"value": "", "visible": False}  # new_item_input update
        ]
    return [
        {"choices": current_items.choices},  # Dropdown update
        {"value": "", "visible": False}  # new_item_input update
    ]

# Gradio Interface
with gr.Blocks() as app:
    try:
        gr.Markdown("# Website Content Generator - Dein KI-Assistent für Webinhalte")
        logger.info("Starte Gradio Interface")
        
        # Definiere die Komponenten für Content-Erstellung außerhalb der Tabs
        briefing_info = get_briefing_info()
        logger.debug(f"Briefing Info geladen: {briefing_info}")
        
        tabs = gr.Tabs()
        with tabs:
            # Briefing Analyse Tab
            with gr.Tab("Briefing Analyse", id="briefing_tab"):
                # Hauptkomponenten
                briefing_input = gr.Textbox(
                    label="Briefing",
                    placeholder="Beschreibe dein Projekt...",
                    lines=5
                )
                analyze_button = gr.Button("Analysieren")
                analysis_output = gr.Textbox(
                    label="Analyse",
                    lines=10,
                    interactive=False
                )
                
                # Antwortbereich
                answers_input = gr.Textbox(
                    label="Deine Antworten",
                    lines=5,
                    visible=False
                )
                submit_answers = gr.Button("Antworten absenden", visible=False)
                next_step_button = gr.Button("Weiter zur Content-Erstellung", visible=False)
                
                # Speichere Zwischenergebnisse
                initial_briefing = gr.State()
                questions_asked = gr.State()
            
            # Content-Erstellung Tab
            with gr.Tab("Content Erstellung", id="content_tab"):
                with gr.Row():
                    company_facts = gr.Textbox(
                        label="Unternehmensfakten",
                        lines=3
                    )
                    location_info = gr.Textbox(
                        label="Standortinformationen",
                        lines=3
                    )
                
                section_type = gr.Dropdown(
                    label="Website-Bereich",
                    choices=["Startseite", "Über uns", "Leistungen", "Kontakt"]
                )
                
                generate_button = gr.Button("Content generieren")
                content_output = gr.Textbox(
                    label="Generierter Content",
                    lines=10,
                    interactive=False
                )
        
        # Event Handler
        analyze_button.click(
            fn=start_briefing_analysis,
            inputs=[briefing_input],
            outputs=[analysis_output]
        ).then(
            fn=lambda: (
                {"visible": True},  # answers_input
                {"visible": True},  # submit_answers
                {"visible": False},  # next_step_button
                {"value": ""},  # analysis_output
                None,  # initial_briefing state
                None   # questions_asked state
            ),
            inputs=[],
            outputs=[answers_input, submit_answers, next_step_button, analysis_output, initial_briefing, questions_asked]
        )
        
        submit_answers.click(
            fn=lambda answers, initial_analysis, questions: (
                process_answers(initial_analysis, questions, answers),
                {"visible": True},   # next_step_button
                {"visible": False},  # answers_input
                {"visible": False}   # submit_answers
            ),
            inputs=[answers_input, analysis_output, analysis_output],
            outputs=[analysis_output, next_step_button, answers_input, submit_answers]
        )
        
        next_step_button.click(
            fn=lambda: {"selected": "content_tab"},
            inputs=[],
            outputs=[tabs]
        )
        
        # Content Generation Event Handler
        generate_button.click(
            fn=create_section_content,
            inputs=[section_type, company_facts, location_info],
            outputs=[content_output]
        )
        
        logger.info("Event Handler erfolgreich konfiguriert")
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Gradio-Oberfläche: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("Starte Anwendung")
        app.launch()
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}", exc_info=True)
        raise 