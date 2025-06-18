from time import time
import flet as ft
from chatbot import ChatBot

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    bot = {"instance": None}


    def send_message(e):
        question = user_input.value.strip()
        system_prompt = system_input.value.strip()
        if not question or not system_prompt:
            return
        
        if bot["instance"] is None:
            bot["instance"] = ChatBot(system_prompt=system_prompt)


        chat_column.controls.append(ft.Text(f"👤 Ти: {question}", size=16))
        page.update()

        start_time = time()
        answer = bot["instance"].ask(question)
        duration = time() - start_time

        chat_column.controls.append(
            ft.Text(f"🤖 Бот: {answer}\n⏱ Отне: {duration:.2f} сек.", size=16, selectable=True)
        )
        user_input.value = ""
        page.update()


    chat_column = ft.Column(expand=True, spacing=10)
    system_input = ft.TextField(
        label="System Prompt (характер на бота)",
        multiline=True,
        value="Ти си мил асистент, който винаги отговаря на български език. Казваш се Иван и си от България.",
        expand=True
    )
    user_input = ft.TextField(label="Въведи съобщение", expand=True, on_submit=send_message)
    send_btn = ft.ElevatedButton("Изпрати", on_click=send_message)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("GGUF Чат Бот", size=24, weight="bold"),
                system_input,
                ft.Row([user_input, send_btn]),
                ft.Divider(),
                chat_column
            ], expand=True),
            padding=20,
            bgcolor=ft.Colors.WHITE
        )
    )

ft.app(target=main)
