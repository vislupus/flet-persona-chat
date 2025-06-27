from time import time
import flet as ft
from chatbot import ChatBot
from history_manager import HistoryManager


class GGUFChatApp:

    BUBBLE_RATIO = 0.7

    def __init__(self, page: ft.Page, persona: dict):
        self.page = page
        self.current_persona = persona
        self._bot = {"instance": None}
        self.history_manager = HistoryManager()
        self.current_chat_messages = []

        self.persona_avatar = ft.CircleAvatar(
            content=ft.Image(src=self.current_persona.get("image_path"), error_content=ft.Icon(ft.Icons.PERSON))
        )
        self.persona_name = ft.Text(self.current_persona.get("name", "Unknown"), size=18, weight=ft.FontWeight.BOLD)

        self.chat_actions_menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(icon=ft.Icons.SAVE_ALT, text="Save Chat", on_click=self._save_chat_click),
                ft.PopupMenuItem(icon=ft.Icons.BOOKMARK_ADD, text="Save as Memory", on_click=self._save_memory_click),
                ft.PopupMenuItem(),  # Divider
                ft.PopupMenuItem(icon=ft.Icons.ADD_COMMENT_ROUNDED, text="New Chat", on_click=self._new_chat_click),
            ]
        )
        
        self.header_container = ft.Container(
            content=ft.ListTile(
                leading=self.persona_avatar,
                title=self.persona_name,
                subtitle=ft.Text("LLM Chat", size=12),
                trailing=self.chat_actions_menu
            ),
            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            height=70
        )

        self.user_input = ft.TextField(
            label="Enter your message", expand=True,
            on_submit=self._send_message, border_radius=10
        )

        self.send_btn = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED, tooltip="Send Message",
            on_click=self._send_message
        )

        self.chat_column = ft.Column(
            expand=True, spacing=10, 
            scroll=ft.ScrollMode.ALWAYS,
            auto_scroll=True,
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
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
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

    @property
    def view(self):
        return self._root
    
    def _save_chat_click(self, e):
        print("Save Chat clicked")
        # In the next step, we will add:
        # self.history_manager.save_chat(self.current_persona['id'], self.current_chat_messages)
        self.page.snack_bar = ft.SnackBar(ft.Text("Chat saved (functionality coming soon)!"), open=True)
        self.page.update()

    def _save_memory_click(self, e):
        print("Save Memory clicked")
        self.page.snack_bar = ft.SnackBar(ft.Text("Save Memory (functionality coming soon)!"), open=True)
        self.page.update()

    def _new_chat_click(self, e):
        print("New Chat clicked")
        # Clear the screen and the in-memory history
        self.chat_column.controls.clear()
        self.current_chat_messages.clear()
        self._bot["instance"] = None # Reset the bot to clear its internal history
        self.page.snack_bar = ft.SnackBar(ft.Text("New chat started."), open=True)
        self.page.update()

    
    def start_new_chat(self, persona: dict):
        self.current_persona = persona
        self._bot["instance"] = None
        
        self.persona_avatar.content = ft.Image(src=self.current_persona.get("image_path"), error_content=ft.Icon(ft.Icons.PERSON))
        self.persona_name.value = self.current_persona.get("name", "Unknown")
        self.chat_column.controls.clear()


    def _on_resize(self, e=None):
        if not self._root.page:
            return

        page_height = self.page.height
        page_width = self.page.width
        
        self.chat_container.height = page_height - (self.header_container.height + self.input_container.height + 40)

        max_width = page_width * self.BUBBLE_RATIO
        
        for row in self.chat_column.controls:
            wrapper = row.controls[0]
            if row.alignment == ft.MainAxisAlignment.START:
                wrapper = row.controls[1]

            if isinstance(wrapper, ft.Container):
                wrapper.width = max_width

        self.page.update()
        

    def _send_message(self, e):
        question = self.user_input.value.strip()
        if not question or not self.current_persona:
            return

        if self._bot["instance"] is None:
            prompt = self.current_persona.get("prompt", "You are a helpful assistant.")
            self._bot["instance"] = ChatBot(system_prompt=prompt)


        self._add_user_bubble(question)
        self.user_input.disabled = True
        self.send_btn.disabled = True
        self.page.update()
        self._scroll_to_bottom() 

        start_time = time()
        answer = self._bot["instance"].ask(question)
        elapsed = time() - start_time

        self._add_bot_bubble(answer, elapsed)
        self.user_input.value = ""
        self.user_input.disabled = False
        self.send_btn.disabled = False
        self.page.update()
        self._scroll_to_bottom() 
        self.user_input.focus()


    def _scroll_to_bottom(self):
        self.page.update()
        self.chat_column.scroll_to(offset=-1, duration=300)


    def _add_user_bubble(self, text: str):
        self.current_chat_messages.append({"role": "user", "content": text})

        bubble = ft.Container(
            content=ft.Markdown(text, selectable=True, extension_set="git-hub-flavored", code_theme="atom-one-dark"),
            padding=10,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=10,
            border=ft.border.all(0.3, ft.Colors.OUTLINE),
        )

        wrapper = ft.Container(
            content=bubble,
            width=self.page.width * self.BUBBLE_RATIO,
            alignment=ft.alignment.center_right,
            margin=ft.margin.only(right=20),
        )

        self.chat_column.controls.append(
            ft.Row([wrapper], alignment=ft.MainAxisAlignment.END)
        )

    def _add_bot_bubble(self, answer: str, elapsed: float):
        self.current_chat_messages.append({"role": "bot", "content": answer})

        bubble = ft.Container(
            content=ft.Markdown(
                f"{answer}\n\n*Response time: {elapsed:.2f}s*", 
                selectable=True, 
                extension_set="git-hub-flavored", 
                code_theme="atom-one-dark"
            ),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_200),
            border_radius=10,
            border=ft.border.all(0.3, ft.Colors.OUTLINE),
        )

        wrapper = ft.Container(
            content=bubble,
            width=self.page.width * self.BUBBLE_RATIO,
            alignment=ft.alignment.center_left,
        )
        
        self.chat_column.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Image(
                            src=self.current_persona.get("image_path"), 
                            fit=ft.ImageFit.COVER, 
                            error_content=ft.Icon(ft.Icons.PERSON)
                        ),
                        width=40, 
                        height=40, 
                        border_radius=20, 
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    wrapper,
                ], 
                alignment=ft.MainAxisAlignment.START, 
                vertical_alignment=ft.CrossAxisAlignment.START, 
                spacing=10
            )
        )