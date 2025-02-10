import gradio as gr
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguration der verfügbaren Agents
AGENTS = {
    'webdesign': {
        'name': 'Webdesign Agent',
        'description': 'KI-gestützte Webdesign-Analyse und Content-Erstellung',
        'port': 8080,
        'icon': '🎨',
        'url': '/agents/webdesign'
    },
    'marketing': {
        'name': 'Marketing Agent',
        'description': 'Marketing-Strategien und Kampagnen-Optimierung',
        'port': 8081,
        'icon': '📈',
        'url': '/agents/marketing'
    },
    'seo': {
        'name': 'SEO Agent',
        'description': 'SEO-Analyse und Optimierungsvorschläge',
        'port': 8082,
        'icon': '🔍',
        'url': '/agents/seo'
    }
}

def create_agent_card(agent_info):
    """Erstellt eine Karte für einen Agent"""
    with gr.Box():
        with gr.Row():
            gr.Markdown(f"# {agent_info['icon']} {agent_info['name']}")
        with gr.Row():
            gr.Markdown(agent_info['description'])
        with gr.Row():
            gr.Button("Agent öffnen", link=agent_info['url'])

# Dashboard erstellen
with gr.Blocks(title="AI Agency Dashboard", theme=gr.themes.Soft()) as dashboard:
    gr.Markdown(
        """
        # 🤖 AI Agency Dashboard
        
        Willkommen im zentralen Dashboard Ihrer AI Agency. Wählen Sie einen der 
        spezialisierten Agenten aus, um dessen Funktionen zu nutzen.
        """
    )
    
    # Grid für Agent-Karten
    with gr.Row():
        for agent_id, agent_info in AGENTS.items():
            with gr.Column():
                create_agent_card(agent_info)
    
    # Footer
    gr.Markdown(
        """
        ---
        © 2024 peter-krause.net | [Impressum](https://peter-krause.net/impressum) | 
        [Datenschutz](https://peter-krause.net/datenschutz)
        """
    )

if __name__ == "__main__":
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=False
    ) 