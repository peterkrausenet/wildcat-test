import os
import gradio as gr
from dotenv import load_dotenv
from agency_swarm import Agency
from .agents.content_creation_agent.agent import ContentCreationAgent
from .agents.webdesign_agent.agent import WebdesignAgent
import logging
import json
import traceback

# Logging-Konfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lade die Umgebungsvariablen
load_dotenv()

# Instanziiere die Agenten
webdesign_agent = WebdesignAgent()
content_agent = ContentCreationAgent()

# Erstelle die Agency
agency = Agency(
    [
        webdesign_agent,  # Entry point agent
        [webdesign_agent, content_agent],  # Kommunikationsfluss
    ],
    shared_instructions="agency_manifesto.md"
)

# Globaler Speicher für das finale Briefing und State-Variablen
complete_briefing = {}
initial_briefing = None
questions_asked = None

def debug_dict(d, prefix=""):
    """Hilfsfunktion zum Debuggen von Dictionaries"""
    try:
        return json.dumps(d, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Fehler beim Serialisieren: {str(e)}"

def analyze_briefing(briefing):
    """Analysiert das Briefing und generiert relevante Verständnisfragen"""
    try:
        # Speichere das ursprüngliche Briefing
        global initial_briefing
        initial_briefing = briefing
        
        questions = webdesign_agent.generate_questions(briefing)
        return questions if questions else "Keine offenen Fragen identifiziert."
    except Exception as e:
        return f"Fehler bei der Fragen-Generierung: {str(e)}"

def start_briefing_analysis(briefing):
    """Startet die Briefing-Analyse mit interaktivem Chat"""
    try:
        # Speichere das ursprüngliche Briefing
        global initial_briefing, questions_asked, complete_briefing
        initial_briefing = briefing
        
        logger.debug(f"Starte Analyse mit Briefing: {briefing[:200]}...")
        
        # Website-Analyse durchführen
        result = webdesign_agent.analyze_briefing(briefing)
        analysis = result["analysis"]
        menu_items = result["menu_items"]
        
        # SEO-Begriffe vorschlagen
        seo_terms = webdesign_agent.suggest_seo_terms(briefing)
        
        # Verständnisfragen generieren
        questions = webdesign_agent.generate_questions(briefing)
        
        # Speichere die Fragen
        questions_asked = questions
        
        # Speichere ALLE Informationen im complete_briefing
        complete_briefing = {
            'original_briefing': briefing,  # Das vollständige Original-Briefing
            'menu_items': menu_items,
            'analysis': analysis,
            'seo_terms': seo_terms,
            'final_analysis': analysis  # Initial gleich der ersten Analyse
        }
        
        logger.debug(f"Gespeichertes Complete Briefing: {debug_dict(complete_briefing)}")
        
        return f"""📋 Briefing-Analyse
=================

{analysis}

🎯 SEO-Optimierung
================
{seo_terms}

❓ Rückfragen zur Klärung
======================
{questions}

Bitte überprüfe die Analyse und beantworte die Rückfragen, damit wir den Content optimal auf deine Bedürfnisse abstimmen können."""

    except Exception as e:
        error_msg = f"Fehler bei der Analyse: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return error_msg

def process_answers(answers):
    """Verarbeitet die Antworten und aktualisiert die Analyse"""
    try:
        logger.debug(f"Verarbeite Antworten: {answers[:100]}...")
        
        if not answers.strip():
            logger.warning("Leere Antworten erhalten")
            return "Bitte beantworte die Rückfragen, um fortzufahren."
        
        global initial_briefing, questions_asked, complete_briefing
        logger.debug(f"Initial Briefing: {initial_briefing[:100]}...")
        logger.debug(f"Gestellte Fragen: {questions_asked}")
        
        # Aktualisiere die Analyse mit den Antworten
        result = webdesign_agent.update_analysis(
            initial_briefing=initial_briefing,
            questions=questions_asked,
            answers=answers
        )
        
        updated_analysis = result["analysis"]
        menu_items = result["menu_items"]
        
        logger.debug(f"Aktualisierte Analyse: {updated_analysis[:100]}...")
        logger.info(f"Extrahierte Menüpunkte: {menu_items}")
        
        # Aktualisiere das complete_briefing mit ALLEN Informationen
        complete_briefing.update({
            'questions_and_answers': {
                'questions': questions_asked,
                'answers': answers
            },
            'final_analysis': updated_analysis,
            'menu_items': menu_items,
            # Original-Briefing und SEO-Terms bleiben erhalten
        })
        
        logger.debug(f"Aktualisiertes Complete Briefing: {debug_dict(complete_briefing)}")
        
        return f"""📋 Aktualisierte Briefing-Analyse
==========================

{updated_analysis}

✅ Die Analyse wurde gespeichert und wird als Grundlage für die Content-Erstellung verwendet."""

    except Exception as e:
        error_msg = f"Fehler bei der Verarbeitung: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return error_msg

def create_content(analysis_result):
    """Erstellt Content basierend auf der Analyse"""
    if not analysis_result.strip():
        return "Bitte führen Sie zuerst eine Analyse durch."
    
    try:
        # Hole das gespeicherte Briefing
        global complete_briefing
        if not complete_briefing:
            return "Bitte führen Sie zuerst eine vollständige Briefing-Analyse durch."
        
        # Generiere Content basierend auf dem kompletten Briefing
        content = content_agent.create_content(complete_briefing)
        return content
    except Exception as e:
        return f"Fehler bei der Content-Erstellung: {str(e)}"

def show_answer_fields(analysis):
    """Zeigt die Antwortfelder an"""
    return gr.update(visible=True), gr.update(visible=True), analysis

def hide_answer_fields_show_next():
    """Blendet die Antwortfelder aus und zeigt den Weiter-Button"""
    return [
        gr.update(visible=False),  # answers_input
        gr.update(visible=False),  # submit_answers
        gr.update(visible=True, value="→ Weiter zur Content-Erstellung")  # next_step_button mit korrektem Text
    ]

def switch_to_content_tab(content):
    """Wechselt zum Content-Tab und zeigt den generierten Content"""
    return gr.Tabs(selected="content_tab"), content

def extract_menu_items(analysis):
    """Extrahiert die Menüpunkte aus der Analyse"""
    try:
        logger.debug(f"Starte Menüpunkt-Extraktion aus Analyse: {analysis[:200]}...")
        
        # Finde den Seitenstruktur-Abschnitt
        structure_start = analysis.find("📑 Seitenstruktur")
        if structure_start == -1:
            structure_start = analysis.lower().find("seitenstruktur")
        
        structure_end = analysis.find("🎯 Zielgruppen-Analyse")
        if structure_end == -1:
            structure_end = analysis.lower().find("zielgruppen")
            if structure_end == -1:
                structure_end = len(analysis)
        
        logger.debug(f"Gefundene Positionen - Start: {structure_start}, Ende: {structure_end}")
        
        if structure_start != -1:
            structure_text = analysis[structure_start:structure_end].strip()
            logger.debug(f"Extrahierter Strukturtext: {structure_text}")
            
            # Extrahiere die Menüpunkte (Zeilen die mit - beginnen)
            menu_items = [line.strip('- *').split(':')[0].strip() 
                         for line in structure_text.split('\n') 
                         if line.strip().startswith(('-', '*'))]
            
            logger.debug(f"Extrahierte Menüpunkte: {menu_items}")
            
            # Wenn keine Menüpunkte gefunden wurden, füge Standardmenüpunkte hinzu
            if not menu_items:
                menu_items = ["Startseite", "Über uns", "Leistungen", "Kontakt"]
                logger.info("Keine Menüpunkte gefunden, verwende Standardmenüpunkte")
            
            return menu_items
        
        logger.warning("Keine Seitenstruktur gefunden, verwende Standardmenüpunkte")
        return ["Startseite", "Über uns", "Leistungen", "Kontakt"]
        
    except Exception as e:
        logger.error(f"Fehler bei der Menüpunkt-Extraktion: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return ["Startseite", "Über uns", "Leistungen", "Kontakt"]

def create_content_and_switch_tab(analysis_result):
    """Wechselt zum Content-Tab und lädt die Menüpunkte"""
    try:
        logger.debug("Starte Tab-Wechsel und Menüpunkt-Ladung")
        
        # Hole die Menüpunkte aus dem complete_briefing
        global complete_briefing
        menu_items = complete_briefing.get('menu_items', ["Startseite", "Über uns", "Leistungen", "Kontakt"])
        
        # Entferne die Asteriske aus den Menüpunkten
        menu_items = [item.strip('*') for item in menu_items]
        
        logger.debug(f"Geladene Menüpunkte: {menu_items}")
        logger.debug(f"Gespeichertes Briefing: {debug_dict(complete_briefing)}")
        
        return [
            "",  # Leerer Content-Output
            gr.update(selected="content_tab"),  # Tab-Wechsel
            gr.Dropdown(choices=menu_items, value=menu_items[0] if menu_items else None),  # Aktualisiere die Menüpunkte im Dropdown
            menu_items,  # Aktualisiere den State
            complete_briefing  # Übergebe das komplette Briefing
        ]
    except Exception as e:
        error_msg = f"Fehler beim Laden der Menüpunkte: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return ["Fehler beim Laden der Menüpunkte: " + str(e),
                gr.update(selected="content_tab"),
                gr.Dropdown(choices=[]),
                [],
                {}]

def update_menu_items(menu_items, new_item):
    """Fügt einen neuen Menüpunkt hinzu oder aktualisiert bestehende"""
    if new_item:
        menu_items = menu_items + [new_item] if menu_items else [new_item]
    return gr.Dropdown(choices=menu_items), menu_items

def remove_menu_item(menu_items, item_to_remove):
    """Entfernt einen Menüpunkt"""
    if item_to_remove in menu_items:
        menu_items.remove(item_to_remove)
    return gr.Dropdown(choices=menu_items), menu_items

def generate_content_for_page(menu_item, num_paragraphs, words_per_paragraph, briefing_data):
    """Generiert Content für einen spezifischen Menüpunkt"""
    try:
        logger.debug(f"Content-Generierung gestartet für Menüpunkt: {menu_item}")
        logger.debug(f"Parameter: {num_paragraphs} Absätze, {words_per_paragraph} Wörter pro Absatz")
        logger.debug(f"Briefing-Daten: {debug_dict(briefing_data)}")
        
        if not menu_item:
            logger.warning("Kein Menüpunkt ausgewählt")
            return "Bitte wählen Sie einen Menüpunkt aus."
            
        if not briefing_data or 'original_briefing' not in briefing_data:
            logger.error("Kein Briefing gefunden")
            return "Fehler: Bitte führen Sie zuerst eine vollständige Briefing-Analyse durch."
        
        # Erstelle ein content_params Dictionary
        content_params = {
            'menu_item': menu_item,
            'num_paragraphs': num_paragraphs,
            'words_per_paragraph': words_per_paragraph
        }
        
        # Füge das content_params zum briefing_data hinzu
        briefing_data['content_params'] = content_params
        
        logger.debug(f"Vollständiges Briefing-Data vor Content-Generierung: {debug_dict(briefing_data)}")
        
        # Rufe die create_content Funktion des ContentCreationAgent auf
        content = content_agent.create_content(briefing_data)
        
        logger.debug(f"Generierter Content: {content[:100]}...")
        return content
        
    except Exception as e:
        error_msg = f"Fehler bei der Content-Generierung: {str(e)}"
        logger.error(error_msg)
        logger.error("Stack Trace:", exc_info=True)
        return error_msg

# Erstelle das Gradio Interface
with gr.Blocks(theme=gr.themes.Default()) as demo:
    # State für das Briefing
    briefing_state = gr.State({})
    
    gr.Markdown("""# 🎨 Website Content Generator

### Dein KI-Assistent für professionelle Webinhalte""")
    
    with gr.Tabs() as tabs:
        # Briefing Analyse Tab
        with gr.Tab("📋 Briefing Analyse", id="briefing_tab"):
            briefing_input = gr.Textbox(
                label="Gib hier dein Briefing ein",
                placeholder="Beschreibe dein Projekt, deine Ziele und Anforderungen...",
                lines=5
            )
            analyze_button = gr.Button("Briefing analysieren", variant="primary")
            analysis_output = gr.Textbox(
                label="Analyse-Ergebnis",
                lines=10,
                show_copy_button=True
            )
            
            # Antwortbereich für Rückfragen
            answers_input = gr.Textbox(
                label="Beantworte hier die Rückfragen",
                placeholder="Gib deine Antworten ein...",
                lines=3,
                visible=False
            )
            submit_answers = gr.Button(
                "Antworten absenden",
                variant="secondary",
                visible=False
            )
            
            # Button für den Übergang zur Content-Erstellung
            next_step_button = gr.Button(
                "→ Weiter zur Content-Erstellung",
                variant="primary",
                visible=False
            )
        
        # Content Erstellung Tab
        with gr.Tab("✍️ Content Erstellung", id="content_tab"):
            with gr.Row():
                with gr.Column(scale=2):
                    # Menüpunkt-Verwaltung
                    menu_items_state = gr.State([])  # Speichert die Menüpunkte
                    menu_dropdown = gr.Dropdown(
                        label="Menüpunkt auswählen",
                        choices=[],
                        interactive=True
                    )
                    with gr.Row():
                        new_menu_item = gr.Textbox(
                            label="Neuer Menüpunkt",
                            placeholder="Namen eingeben..."
                        )
                        add_menu_btn = gr.Button("Hinzufügen", size="sm")
                        remove_menu_btn = gr.Button("Entfernen", size="sm", variant="stop")
                    
                    # Content-Parameter
                    with gr.Group():
                        gr.Markdown("### Content-Parameter")
                        num_paragraphs = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=3,
                            step=1,
                            label="Anzahl Absätze"
                        )
                        words_per_paragraph = gr.Slider(
                            minimum=50,
                            maximum=500,
                            value=150,
                            step=10,
                            label="Wörter pro Absatz (EXAKT)"
                        )
                    
                    # Generate Button
                    generate_btn = gr.Button(
                        "Content generieren",
                        variant="primary"
                    )
                
                with gr.Column(scale=3):
                    # Content Output
                    content_output = gr.TextArea(
                        label="Generierter Content",
                        lines=15,
                        show_copy_button=True
                    )
    
    # Event Handler
    analyze_button.click(
        fn=start_briefing_analysis,
        inputs=[briefing_input],
        outputs=[analysis_output]
    ).then(
        fn=show_answer_fields,
        inputs=[analysis_output],
        outputs=[answers_input, submit_answers, next_step_button]
    )
    
    submit_answers.click(
        fn=process_answers,
        inputs=[answers_input],
        outputs=[analysis_output]
    ).then(
        fn=hide_answer_fields_show_next,
        outputs=[answers_input, submit_answers, next_step_button]
    )
    
    next_step_button.click(
        fn=create_content_and_switch_tab,
        inputs=[analysis_output],
        outputs=[
            content_output,
            tabs,
            menu_dropdown,
            menu_items_state,
            briefing_state
        ]
    )

    # Content Tab Event Handler
    add_menu_btn.click(
        fn=update_menu_items,
        inputs=[menu_items_state, new_menu_item],
        outputs=[menu_dropdown, menu_items_state]
    ).then(
        fn=lambda x: "",  # Leere das Textfeld nach dem Hinzufügen
        outputs=[new_menu_item]
    )
    
    remove_menu_btn.click(
        fn=remove_menu_item,
        inputs=[menu_items_state, menu_dropdown],
        outputs=[menu_dropdown, menu_items_state]
    )
    
    generate_btn.click(
        fn=generate_content_for_page,
        inputs=[
            menu_dropdown,
            num_paragraphs,
            words_per_paragraph,
            briefing_state  # Verwende den briefing_state anstelle von complete_briefing
        ],
        outputs=[content_output]
    )

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7861
    ) 