import flet as ft


class AppViews:
    @staticmethod
    def get_upload_view(handle_upload_callback, processing_flag=False):
        """
        Vista inicial de carga.
        Se usaron strings para iconos y colores para compatibilidad con Flet 0.28.3
        """
        content = [
            ft.Icon(name="school", size=100, color="blue"),
            ft.Text("EvaluadorIA", size=30, weight="bold"),
            ft.Text("Sube tu PDF y genera un examen con IA", size=16),
            ft.Divider(height=20, color="transparent"),
        ]

        if processing_flag:
            content.append(ft.ProgressRing())
            content.append(ft.Text("Leyendo PDF y consultando a Groq... espere..."))
        else:
            btn = ft.ElevatedButton(
                "Seleccionar Archivo PDF",
                icon="upload_file",  # String directo
                on_click=lambda _: handle_upload_callback(),
                height=50,
                width=250,
            )
            content.append(btn)

        return ft.View(
            "/",
            controls=[
                ft.Container(
                    content=ft.Column(
                        content,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ],
        )

    @staticmethod
    def get_quiz_view(questions, handle_submit_callback, update_answer_callback):
        """Vista del examen"""
        controls = [ft.Text("Examen Generado", size=24, weight="bold")]

        for q in questions:
            # RadioGroup para opciones
            options_ctrl = ft.RadioGroup(
                content=ft.Column(
                    [ft.Radio(value=opt, label=opt) for opt in q["options"]]
                ),
                on_change=lambda e, q_id=q["id"]: update_answer_callback(
                    q_id, e.control.value
                ),
            )

            # Tarjeta de pregunta
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"{q['id']}. {q['question']}", weight="bold", size=16
                            ),
                            options_ctrl,
                        ]
                    ),
                    padding=20,
                )
            )
            controls.append(card)

        # Botón de finalizar
        submit_btn = ft.ElevatedButton(
            "Calificar Examen",
            on_click=lambda _: handle_submit_callback(),
            bgcolor="green",
            color="white",
            height=50,
        )
        controls.append(submit_btn)

        return ft.View(
            "/quiz",
            controls=[ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True)],
        )

    @staticmethod
    def get_result_view(score, restart_callback):
        """Vista de resultados"""
        color_theme = "green" if score >= 60 else "red"
        msg = "¡Aprobado!" if score >= 60 else "Reprobado"
        icon_name = "check_circle" if score >= 60 else "warning"

        return ft.View(
            "/results",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(name=icon_name, size=100, color=color_theme),
                            ft.Text(
                                f"{score}/100",
                                size=60,
                                weight="bold",
                                color=color_theme,
                            ),
                            ft.Text(msg, size=20),
                            ft.Divider(),
                            ft.ElevatedButton(
                                "Nuevo Examen", on_click=lambda _: restart_callback()
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ],
        )
