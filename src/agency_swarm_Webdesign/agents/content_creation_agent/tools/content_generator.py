from agency_swarm.tools import BaseTool
from pydantic import Field
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator(BaseTool):
    """
    Ein Tool zur Generierung von SEO-optimierten Inhalten basierend auf einem gegebenen Prompt.
    """
    prompt: str = Field(
        ..., description="Der Prompt für die Content-Generierung"
    )

    def run(self):
        """
        Generiert Content basierend auf dem gegebenen Prompt.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Du bist ein professioneller Content Creator, der SEO-optimierte und ansprechende Texte erstellt."},
                    {"role": "user", "content": self.prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Fehler bei der Content-Generierung: {str(e)}"

if __name__ == "__main__":
    # Test des Tools
    generator = ContentGenerator(prompt="Schreibe einen kurzen Text über Content Marketing.")
    print(generator.run())

content_generator = ContentGenerator 