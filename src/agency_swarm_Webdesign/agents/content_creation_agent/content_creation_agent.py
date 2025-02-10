import logging
import openai

class ContentCreationAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_content(self, briefing_data):
        """
        Generiert Content basierend auf den Briefing-Daten und spezifischen Parametern
        """
        try:
            self.logger.debug("Starte Content-Generierung mit Briefing-Daten")
            
            # Extrahiere die Parameter aus dem briefing_data
            content_params = briefing_data.get('content_params', {})
            menu_item = content_params.get('menu_item')
            num_paragraphs = content_params.get('num_paragraphs', 3)
            words_per_paragraph = content_params.get('words_per_paragraph', 100)
            
            original_briefing = briefing_data.get('original_briefing', '')
            final_analysis = briefing_data.get('final_analysis', '')
            
            self.logger.debug(f"Parameter für Content-Generierung:")
            self.logger.debug(f"Menüpunkt: {menu_item}")
            self.logger.debug(f"Anzahl Absätze: {num_paragraphs}")
            self.logger.debug(f"Wörter pro Absatz: {words_per_paragraph}")
            self.logger.debug(f"Original Briefing vorhanden: {bool(original_briefing)}")
            self.logger.debug(f"Finale Analyse vorhanden: {bool(final_analysis)}")
            
            if not original_briefing or not final_analysis:
                raise ValueError("Briefing oder Analyse fehlt")
            
            # Erstelle den Prompt für die Content-Generierung
            prompt = self._create_content_prompt(
                menu_item=menu_item,
                num_paragraphs=num_paragraphs,
                words_per_paragraph=words_per_paragraph,
                briefing=original_briefing,
                analysis=final_analysis
            )
            
            # Generiere den Content mit OpenAI
            content = self._generate_with_openai(prompt)
            
            self.logger.debug(f"Generierter Content: {content[:200]}...")
            return content
            
        except Exception as e:
            error_msg = f"Fehler bei der Content-Generierung: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error("Stack Trace:", exc_info=True)
            return error_msg
            
    def _create_content_prompt(self, menu_item, num_paragraphs, words_per_paragraph, briefing, analysis):
        """Erstellt den Prompt für die Content-Generierung"""
        prompt = f"""
        Erstelle professionellen Website-Content basierend auf dem folgenden Briefing und der Analyse.
        
        ORIGINAL BRIEFING:
        ================
        {briefing}
        
        FINALE ANALYSE:
        =============
        {analysis}
        
        AUFGABE:
        =======
        Erstelle Content für die Seite "{menu_item}" mit EXAKT folgenden Spezifikationen:
        - GENAU {num_paragraphs} Absätze
        - EXAKT {words_per_paragraph} Wörter pro Absatz (KEINE Abweichung erlaubt!)
        
        WICHTIGE ANWEISUNGEN:
        ==================
        1. Nutze ALLE Informationen aus dem Original-Briefing UND der Analyse
        2. Der Content muss perfekt zur Seite "{menu_item}" passen
        3. Verwende einen professionellen, aber zugänglichen Schreibstil
        4. Integriere wichtige Keywords und Themen aus BEIDEN Quellen
        5. Stelle sicher, dass der Content zur Gesamtstrategie passt
        6. Berücksichtige die Zielgruppen-Analyse
        7. Formatiere den Text mit passenden Zwischenüberschriften
        8. KRITISCH WICHTIG: 
           - Jeder Absatz MUSS EXAKT {words_per_paragraph} Wörter enthalten
           - Zähle die Wörter mehrfach nach
           - Ein Wort ist durch Leerzeichen getrennt
           - Überschriften zählen nicht mit
        
        FORMAT:
        ======
        # {menu_item}
        
        [SEO-optimierte Hauptüberschrift]
        
        ## [Erste Zwischenüberschrift]
        [Erster Absatz - EXAKT {words_per_paragraph} Wörter]
        
        ## [Weitere Zwischenüberschriften]
        [Weitere Absätze - jeweils EXAKT {words_per_paragraph} Wörter]
        
        HINWEIS: Zähle die Wörter in jedem Absatz mehrfach nach. Bei Abweichung wird der Content abgelehnt!
        """
        return prompt
        
    def _generate_with_openai(self, prompt):
        """Generiert Content mit OpenAI API"""
        try:
            # Berechne die benötigten Tokens basierend auf der Wortanzahl
            total_words = int(self.params.num_paragraphs * self.params.words_per_paragraph * 1.5)  # 1.5 für Overhead
            max_tokens = max(4000, min(total_words * 4, 8000))  # Erhöhte Token-Limits
            
            self.logger.debug(f"Content-Generierung mit {self.params.num_paragraphs} Absätzen und {self.params.words_per_paragraph} Wörtern pro Absatz (±5% Toleranz)")
            self.logger.debug(f"Erwartete Gesamtwortanzahl: {self.params.num_paragraphs * self.params.words_per_paragraph} (±5% Toleranz)")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"""Du bist ein professioneller Content-Ersteller für Webseiten.
                    WICHTIG: 
                    - Jeder Absatz soll MÖGLICHST GENAU {self.params.words_per_paragraph} Wörter enthalten (±5% Toleranz)
                    - Erstelle GENAU {self.params.num_paragraphs} Absätze
                    - Die Gesamtwortanzahl soll MÖGLICHST GENAU {self.params.num_paragraphs * self.params.words_per_paragraph} Wörter sein
                    - Zähle die Wörter in jedem Absatz mehrfach nach
                    - Ein Wort ist durch Leerzeichen getrennt
                    - Überschriften zählen NICHT zu den Wörtern"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            # Validiere die Anzahl der Absätze und Wörter
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
            
            self.logger.debug(f"Anzahl generierter Absätze: {len(paragraphs)} (Soll: {self.params.num_paragraphs})")
            
            if len(paragraphs) != self.params.num_paragraphs:
                self.logger.warning(f"Falsche Anzahl Absätze: {len(paragraphs)} (Soll: {self.params.num_paragraphs})")
                return self._generate_with_openai(prompt)
            
            # Überprüfe die Wortanzahl in jedem Absatz
            total_words = 0
            allowed_deviation = self.params.words_per_paragraph * 0.05  # 5% Toleranz
            
            for i, para in enumerate(paragraphs, 1):
                words = para.split()
                word_count = len(words)
                total_words += word_count
                
                self.logger.debug(f"Absatz {i}: {word_count} Wörter (Soll: {self.params.words_per_paragraph} ±{int(allowed_deviation)})")
                
                # Überprüfe ob die Wortanzahl innerhalb der Toleranz liegt
                if abs(word_count - self.params.words_per_paragraph) > allowed_deviation:
                    self.logger.warning(f"Absatz {i} weicht zu stark ab: {word_count} Wörter (Toleranzbereich: {self.params.words_per_paragraph - int(allowed_deviation)} bis {self.params.words_per_paragraph + int(allowed_deviation)})")
                    return self._generate_with_openai(prompt)
            
            # Überprüfe die Gesamtwortanzahl
            expected_total = self.params.num_paragraphs * self.params.words_per_paragraph
            total_allowed_deviation = expected_total * 0.05  # 5% Toleranz für Gesamtwortanzahl
            
            self.logger.debug(f"Gesamtwortanzahl: {total_words} (Soll: {expected_total} ±{int(total_allowed_deviation)})")
            
            if abs(total_words - expected_total) > total_allowed_deviation:
                self.logger.warning(f"Gesamtwortanzahl weicht zu stark ab: {total_words} (Toleranzbereich: {expected_total - int(total_allowed_deviation)} bis {expected_total + int(total_allowed_deviation)})")
                return self._generate_with_openai(prompt)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Content-Generierung: {str(e)}")
            return f"Fehler bei der Content-Generierung: {str(e)}" 