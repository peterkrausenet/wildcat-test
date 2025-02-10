from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SEOResearcher(BaseTool):
    """
    Tool zur SEO-Recherche und Keyword-Analyse.
    Analysiert Mitbewerber und identifiziert relevante Keywords.
    """
    
    industry: str = Field(
        ..., 
        description="Die zu analysierende Branche"
    )
    target_audience: str = Field(
        ...,
        description="Die Zielgruppe für die Analyse"
    )
    competitors: List[str] = Field(
        ..., 
        description="Liste der Mitbewerber-URLs"
    )
    
    def _analyze_competitor_content(self, url: str) -> Dict:
        """
        Analysiert den Content eines Mitbewerbers
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Text extrahieren
            text = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
            
            # Meta-Tags analysieren
            meta_description = soup.find('meta', {'name': 'description'})
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            
            return {
                'url': url,
                'text': text[:5000],  # Begrenzen auf 5000 Zeichen
                'meta_description': meta_description.get('content') if meta_description else '',
                'meta_keywords': meta_keywords.get('content') if meta_keywords else ''
            }
        except Exception as e:
            print(f"Fehler beim Analysieren von {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e)
            }
    
    def run(self) -> Dict:
        """
        Führt die SEO-Recherche durch
        """
        try:
            # Mitbewerber-Analyse
            competitor_data = []
            for url in self.competitors:
                data = self._analyze_competitor_content(url)
                competitor_data.append(data)
            
            # Prompt für die Keyword-Analyse erstellen
            prompt = f"""
            Führe eine SEO-Analyse für folgende Parameter durch:
            
            Branche: {self.industry}
            Zielgruppe: {self.target_audience}
            
            Basierend auf den folgenden Mitbewerber-Daten:
            {json.dumps(competitor_data, indent=2, ensure_ascii=False)}
            
            Erstelle eine strukturierte Analyse mit folgenden Punkten:
            1. Hauptkeywords: Die wichtigsten Keywords und deren Relevanz
            2. Themen: Häufig behandelte Themen und Schwerpunkte
            3. Nischen: Potenzielle Nischen oder unterrepräsentierte Themen
            4. Empfehlungen: Konkrete Vorschläge für die Content-Strategie
            
            Formatiere die Antwort als JSON mit den oben genannten Kategorien als Schlüssel.
            """
            
            # OpenAI API für die Analyse nutzen
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein SEO-Experte mit Fokus auf Content-Strategie. Antworte immer in korrektem JSON-Format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Antwort verarbeiten
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "status": "success",
                "industry": self.industry,
                "target_audience": self.target_audience,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"Fehler bei der Analyse: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    # Test
    researcher = SEOResearcher(
        industry="Webdesign",
        target_audience="Kleine und mittlere Unternehmen in München",
        competitors=[
            "https://www.pixelart.at",
            "https://www.websitebutler.de"
        ]
    )
    result = researcher.run()
    print(json.dumps(result, indent=2, ensure_ascii=False)) 