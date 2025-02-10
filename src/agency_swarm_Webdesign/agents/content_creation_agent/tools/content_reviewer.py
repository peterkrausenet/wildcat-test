from agency_swarm.tools import BaseTool
from pydantic import Field
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ContentReviewer(BaseTool):
    """
    Ein Tool zur Überprüfung und Optimierung von Content auf Qualität, SEO und Lesbarkeit.
    """
    content: str = Field(
        ..., description="Der zu überprüfende Content"
    )
    criteria: str = Field(
        default="SEO, Lesbarkeit, Grammatik, Stil",
        description="Die Kriterien für die Überprüfung"
    )

    def run(self):
        """
        Überprüft den Content basierend auf den angegebenen Kriterien.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein Content-Reviewer mit Expertise in SEO, Lesbarkeit und Textqualität."},
                    {"role": "user", "content": f"""Überprüfe folgenden Content basierend auf diesen Kriterien: {self.criteria}

Content:
{self.content}

Gib eine strukturierte Analyse und Verbesserungsvorschläge."""}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Fehler bei der Content-Überprüfung: {str(e)}"

if __name__ == "__main__":
    # Test des Tools
    reviewer = ContentReviewer(
        content="Willkommen auf unserer Webseite. Wir bieten Webdesign an.",
        criteria="SEO, Lesbarkeit, Call-to-Action"
    )
    print(reviewer.run())

content_reviewer = ContentReviewer 