import flet as ft
import sys
import os

# Esto permite importar desde carpetas hermanas subiendo un nivel en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Apunta a la carpeta 'src'
sys.path.append(parent_dir)

from models.models import QuizModel
from views.views import AppViews


class QuizController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.model = QuizModel()
        self.page.title = "Examen - Flet & LangChain"
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # Configurar FilePicker
        self.file_picker = ft.FilePicker(on_result=self.on_file_upload)
        self.page.overlay.append(self.file_picker)

        # Rutas
        self.page.on_route_change = self.route_change
        self.page.go("/")

    def route_change(self, route):
        self.page.views.clear()

        if self.page.route == "/":
            self.page.views.append(AppViews.get_upload_view(self.open_file_dialog))

        elif self.page.route == "/processing":
            self.page.views.append(AppViews.get_upload_view(None, processing_flag=True))

        elif self.page.route == "/quiz":
            self.page.views.append(
                AppViews.get_quiz_view(
                    self.model.questions, self.submit_quiz, self.record_answer
                )
            )

        elif self.page.route == "/results":
            self.page.views.append(
                AppViews.get_result_view(self.model.score, self.restart_app)
            )

        self.page.update()

    def open_file_dialog(self):
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["pdf"])

    def on_file_upload(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.page.go("/processing")
            self.page.update()

            # Lógica
            self.model.extract_text_from_pdf(file_path)
            success = self.model.generate_questions()

            if success:
                self.page.go("/quiz")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Error generando preguntas"))
                self.page.snack_bar.open = True
                self.page.go("/")

    def record_answer(self, question_id, answer_value):
        self.model.user_answers[question_id] = answer_value

    def submit_quiz(self):
        self.model.calculate_score()
        self.page.go("/results")

    def restart_app(self):
        self.model = QuizModel()
        self.page.go("/")


def main(page: ft.Page):
    controller = QuizController(page)


if __name__ == "__main__":
    ft.app(target=main)
