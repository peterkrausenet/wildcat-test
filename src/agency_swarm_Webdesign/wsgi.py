from app import demo
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Stelle sicher, dass der OpenAI API Key gesetzt ist
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY muss in der .env Datei gesetzt sein")
    
    # Starte die Anwendung
    demo.launch(
        server_name="0.0.0.0",  # Erlaube externe Verbindungen
        server_port=8080,  # Port kann angepasst werden
        share=False,
        auth=None  # Hier können Sie Basic Auth hinzufügen
    ) 