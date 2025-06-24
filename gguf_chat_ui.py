from time import time
import flet as ft
from chatbot import ChatBot


class GGUFChatApp:

    BUBBLE_RATIO = 0.7
    LONG_MSG_THRESHOLD = 150

    def __init__(self, page: ft.Page, mount_to: ft.Control | None = None):
        self.page = page

        self._bot = {"instance": None}

        self.system_input = ft.TextField(
            label="System Prompt",
            multiline=True,
            value=(
                "Ти си мил асистент, който винаги отговаря на български език."
                "Ти си момиче на 24 години и си от България. Казваш се Марта и много харесваш котките."
            ),
            expand=True,
            border_radius=10
        )

        self.user_input = ft.TextField(
            label="Въведи съобщение",
            expand=True,
            on_submit=self._send_message,
            border_radius=10
        )

        self.send_btn = ft.ElevatedButton(
            "Изпрати",
            on_click=self._send_message,
            style=ft.ButtonStyle(
                padding=10,
                shape=ft.ContinuousRectangleBorder(radius=10),
            ),
        )

        self.chat_column = ft.Column(
            expand=True, 
            spacing=10, 
            scroll=ft.ScrollMode.ALWAYS,
            auto_scroll=True,
        )

        self.header_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("GGUF Чат Бот", size=24, weight="bold"),
                    self.system_input,
                ]
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            height=115,
        )

        self.chat_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=self.chat_column,
                        padding=ft.padding.only(right=10),
                        expand=True,
                    )
                ],
            ),
            expand=True,
            padding=ft.padding.only(left=20, top=10, bottom=10),
            bgcolor=ft.Colors.BLUE_50,
            width=float("inf"),
        )

        self.input_container = ft.Container(
            content=ft.Row([self.user_input, self.send_btn]),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            height=80,
        )

        self._root = ft.Column(
            [
                self.header_container,
                ft.Divider(height=1),
                self.chat_container,
                ft.Divider(height=1),
                self.input_container,
            ],
            expand=True,
            spacing=0,
        )

        if mount_to is not None:
            mount_to.content = self._root

        self._on_resize(self.page)

    @property
    def view(self):
        return self._root

    def _on_resize(self, e):
        if not self._root.page:
            return
        
        self._resize_chat_container(e)
        self._update_bubble_widths()
        self._scroll_to_bottom() 

    def _resize_chat_container(self, e):
        self.chat_container.height = (
            e.height - (self.header_container.height + self.input_container.height)
        )
        self.chat_container.update()

    def _update_bubble_widths(self):
        max_width = self.page.width * self.BUBBLE_RATIO
        for row in self.chat_column.controls:
            for ctrl in row.controls:
                if isinstance(ctrl, ft.Container) and isinstance(ctrl.content, ft.Markdown):
                    text_len = len(ctrl.content.value or "")
                    ctrl.width = max_width if text_len > self.LONG_MSG_THRESHOLD else None
        self.chat_column.update()

    def _send_message(self, e):
        question = self.user_input.value.strip()
        system_prompt = self.system_input.value.strip()
        if not question or not system_prompt:
            return

        if self._bot["instance"] is None:
            self._bot["instance"] = ChatBot(system_prompt=system_prompt)


        self._add_user_bubble(question)
        self._scroll_to_bottom() 
        self.user_input.disabled = True
        self.send_btn.disabled = True
        self.page.update()

        start_time = time()
        answer = self._bot["instance"].ask(question)
        elapsed = time() - start_time

        self._add_bot_bubble(answer, elapsed)
        self._scroll_to_bottom() 
        self.user_input.value = ""
        self.user_input.disabled = False
        self.send_btn.disabled = False
        self.page.update()
        self.user_input.focus()


    def _scroll_to_bottom(self):
        self.page.update()
        self.chat_column.scroll_to(offset=-1, duration=300)

    def _bubble_width(self, text: str) -> float | None:
        return (
            self.page.width * self.BUBBLE_RATIO
            if len(text) > self.LONG_MSG_THRESHOLD
            else None
        )

    def _add_user_bubble(self, text: str):
        self.chat_column.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Markdown(text, selectable=True,),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=10,
                        alignment=ft.alignment.center_right,
                        width=self._bubble_width(text),
                        border=ft.border.all(0.3, ft.Colors.OUTLINE),
                        margin=ft.margin.only(right=20),
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )

    def _add_bot_bubble(self, answer: str, elapsed: float):
        self.chat_column.controls.append(
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
                        content=ft.Markdown(
                            f"{answer}\n\n_⏱ Отне: {elapsed:.2f} сек._",
                            selectable=True,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                        alignment=ft.alignment.center_left,
                        width=self._bubble_width(answer),
                        border=ft.border.all(0.3, ft.Colors.OUTLINE),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10,
            )
        )
