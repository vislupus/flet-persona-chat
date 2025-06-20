from time import time
import flet as ft
from chatbot import ChatBot

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    bot = {"instance": None}

    def send_message(e):
        question = user_input.value.strip()
        system_prompt = system_input.value.strip()
        if not question or not system_prompt:
            return
        
        if bot["instance"] is None:
            bot["instance"] = ChatBot(system_prompt=system_prompt)

        user_input.disabled = True
        user_input.value = ""
        send_btn.disabled = True
        page.update()


        chat_column.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Markdown(question),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_100,
                    border_radius=10,
                    alignment=ft.alignment.center_right,
                    width=page.width*0.7 if len(question) > 200 else None,
                )
            ], alignment=ft.MainAxisAlignment.END)
        )
        page.update()
        chat_column.scroll_to(offset=-1, duration=300)
        user_input.focus()

        start_time = time()
        answer = bot["instance"].ask(question)
        duration = time() - start_time

        chat_column.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Image(
                            src=r"assets\ComfyUI_00347_.png",
                            fit=ft.ImageFit.COVER,
                        ),
                        width=30,
                        height=30,
                        border_radius=15,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Container(
                        content=ft.Markdown(f"{answer}\n\n_⏱ Отне: {duration:.2f} сек._"),
                        padding=10,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                        alignment=ft.alignment.center_left,
                        width=page.width*0.7 if len(answer) > 200 else None,
                    )
                ], 
                alignment=ft.MainAxisAlignment.START, 
                vertical_alignment=ft.CrossAxisAlignment.START, 
                spacing=10
            )
        )

        user_input.value = ""
        user_input.disabled = False
        send_btn.disabled = False
        page.update()

        chat_column.scroll_to(offset=-1, duration=300)
        user_input.focus()


    chat_column = ft.Column(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    chat_container = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=chat_column,
                    padding=ft.padding.only(right=20),
                    expand=True,
                )
            ], 
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        expand=True,
        padding=ft.padding.only(left=20, top=10, bottom=10),
        bgcolor=ft.Colors.BLUE_50,
        width=float("inf"),
    )

    system_input = ft.TextField(
        label="System Prompt (характер на бота)",
        multiline=True,
        value="Ти си мил асистент, който винаги отговаря на български език. Казваш се Иван и си от България.",
        expand=True
    )
    user_input = ft.TextField(label="Въведи съобщение", expand=True, on_submit=send_message)
    send_btn = ft.ElevatedButton(
        "Изпрати", 
        on_click=send_message, 
        style=ft.ButtonStyle(
            padding=10,
            shape=ft.ContinuousRectangleBorder(radius=10)
        )
    )

    header_container = ft.Container(
        content=ft.Column([
            ft.Text("GGUF Чат Бот", size=24, weight="bold"),
            system_input,
        ]),
        padding=10,
        bgcolor=ft.Colors.GREY_50,
        height=115,
    )

    input_container = ft.Container(
        content=ft.Row([user_input, send_btn]),
        padding=10,
        bgcolor=ft.Colors.GREY_50,
        height=80,
    )

    chat_container.height = page.height - (header_container.height + input_container.height)



    def update_chat_height(e):
        header_height = header_container.height
        input_height = input_container.height
        chat_container.height = e.height-(header_height+input_height)
        chat_container.update()

    page.on_resized = update_chat_height

    def show(e):
        print(e.data)

    page.add(
        ft.Column([
            header_container,
            ft.Divider(height=1),
            chat_container,
            ft.Divider(height=1),
            input_container
        ], 
        expand=True,
        spacing=0,
        )
    )

ft.app(target=main, assets_dir="assets")
