from agency_swarm.tools import BaseTool
from pydantic import Field
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class SEOResearcher(BaseTool):
    """
    Ein Tool zur Analyse und Vorschlag von SEO-relevanten Begriffen für eine bestimmte Branche oder ein Thema.
    """
    text: str = Field(
        ..., description="Der Text oder die Branchenbeschreibung für die SEO-Analyse"
    )

    def suggest_industry_terms(self, text):
        """
        Schlägt SEO-relevante Begriffe für eine bestimmte Branche vor.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein SEO-Experte. Analysiere den Text und schlage relevante Keywords vor."},
                    {"role": "user", "content": f"Analysiere folgenden Text und schlage relevante SEO-Keywords vor:\n\n{text}"}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Fehler bei der SEO-Analyse: {str(e)}"

    def run(self):
        """
        Führt die SEO-Analyse durch.
        """
        return self.suggest_industry_terms(self.text)

if __name__ == "__main__":
    # Test des Tools
    researcher = SEOResearcher(text="Webdesign Agentur für kleine und mittlere Unternehmen")
    print(researcher.run())

seo_researcher = SEOResearcher 