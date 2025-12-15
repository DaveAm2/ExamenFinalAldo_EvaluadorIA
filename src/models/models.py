import os
import json
from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class QuizModel:
    def __init__(self):
        self.pdf_text = ""
        self.questions = []
        self.user_answers = {}
        self.score = 0

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERROR CRÍTICO: No se encontró GROQ_API_KEY en .env")

        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.1-8b-instant",
            api_key=api_key,
        )

    def extract_text_from_pdf(self, file_path):
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            # Limpiamos espacios y limitamos caracteres
            self.pdf_text = text.strip()[:30000]
            print(f"--- DEBUG: Caracteres extraídos: {len(self.pdf_text)} ---")

            if len(self.pdf_text) < 50:
                return False
            return True
        except Exception as e:
            print(f"Error leyendo PDF: {e}")
            return False

    def generate_questions(self):
        # --- PROMPT REFORZANDO CANTIDAD Y EXACTITUD
        template = """
        Eres un generador de exámenes estricto.
        
        INSTRUCCIONES OBLIGATORIAS:
        1. Genera EXACTAMENTE 5 preguntas (Ni 4, ni 6). Es imperativo que sean 5.
        2. El formato de salida debe ser SOLO un JSON válido (array de objetos).
        3. El campo "correct_answer" debe ser COPIA EXACTA del texto de la opción correcta.
        
        TEXTO BASE:
        "{text}"
        
        FORMATO JSON (Array de 5 objetos):
        [
            {{
                "id": 1,
                "question": "¿Pregunta?",
                "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
                "correct_answer": "Opción A"
            }},
            ... (hasta llegar al id: 5)
        ]
        """

        prompt = PromptTemplate(template=template, input_variables=["text"])
        chain = prompt | self.llm

        try:
            print("--- DEBUG: Solicitando 5 preguntas a Groq... ---")
            response = chain.invoke({"text": self.pdf_text})
            raw_content = response.content.strip()

            # Limpieza del JSON
            start_index = raw_content.find("[")
            end_index = raw_content.rfind("]")

            if start_index != -1 and end_index != -1:
                json_clean = raw_content[start_index : end_index + 1]
                data = json.loads(json_clean)

                # --- CONTROL DE CALIDAD DE CANTIDA ---
                if len(data) > 5:
                    print(
                        f"--- AVISO: La IA generó {len(data)} preguntas. Recortando a 5. ---"
                    )
                    self.questions = data[:5]  # Recortamos si se pasó
                else:
                    self.questions = data

                print(
                    f"--- DEBUG: Total final de preguntas cargadas: {len(self.questions)} ---"
                )
                return True
            else:
                print("Error: No se encontraron corchetes JSON.")
                return False

        except Exception as e:
            print(f"Error procesando IA: {e}")
            return False

    def calculate_score(self):
        """Calcula el puntaje comparando strings limpios."""
        print("\n--- DEBUG: INICIANDO EVALUACIÓN ---")
        correct_count = 0

        for q in self.questions:
            q_id = q["id"]

            user_val = str(self.user_answers.get(q_id, "")).strip()
            correct_val = str(q["correct_answer"]).strip()

            print(f"P{q_id} | Usuario: '{user_val}' | Correcta: '{correct_val}'")

            # Comparación exacta o parcial aceptable
            if user_val == correct_val:
                correct_count += 1
            elif len(correct_val) > 5 and (
                correct_val in user_val or user_val in correct_val
            ):
                correct_count += 1

        if self.questions:
            self.score = int((correct_count / len(self.questions)) * 100)
        else:
            self.score = 0

        print(f"--- RESULTADO: {self.score}/100 ---\n")
        return self.score