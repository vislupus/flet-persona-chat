import flet as ft
from chatbot import ask_bot

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    chat_column = ft.Column(expand=True, spacing=10)
    user_input = ft.TextField(label="Въведи съобщение", expand=True)

    def send_message(e):
        question = user_input.value.strip()
        if not question:
            return
        
        chat_column.controls.append(ft.Text(f"👤 Ти: {question}", size=16))
        page.update()

        answer = ask_bot(question)
        chat_column.controls.append(ft.Text(f"🤖 Бот: {answer}", size=16, selectable=True))
        user_input.value = ""
        page.update()

    send_btn = ft.ElevatedButton("Изпрати", on_click=send_message)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("GGUF Чат Бот", size=24, weight="bold"),
                ft.Row([user_input, send_btn]),
                ft.Divider(),
                chat_column
            ], expand=True),
            padding=20,
            bgcolor=ft.Colors.WHITE
        )
    )

ft.app(target=main)
