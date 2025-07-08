import flet as ft
from history_manager import HistoryManager
from persona_selector_ui import PersonaManager
from datetime import datetime


class ChatsViewComponent:
    def __init__(self, page: ft.Page, on_chat_select: callable):
        self.page = page
        self.on_chat_select = on_chat_select
        self.history_manager = HistoryManager()
        self.persona_manager = PersonaManager()

        self.chats_by_date = {}
        self.chats_list_container = ft.Column(
                expand=True, 
                spacing=15, 
            )

        self._root = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=28),
                            ft.Text(
                                "Saved Chats",
                                theme_style=ft.TextThemeStyle.HEADLINE_SMALL,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center_left,
                    padding=10
                ),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.chats_list_container,
                                padding=ft.padding.only(right=20),
                            ),
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    padding=ft.padding.only(left=10, right=10, top=0, bottom=10),
                    expand=True,
                )
            ],
            expand=True,
            spacing=5,
        )
        
    @property
    def view(self) -> ft.Control:
        return self._root

    def _show_delete_confirmation(self, chat_id: str, title: str):
        def confirm_delete(e):
            self.history_manager.delete_chat(chat_id)
            self.update_view()
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete '{title}'?"),
            actions=[
                ft.TextButton(
                    "Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: setattr(dlg, "open", False)
                    or self.page.update(),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def update_view(self):
        self.chats_list_container.controls.clear()
        all_chats = self.history_manager.load_chats()
        all_personas = {p["id"]: p for p in self.persona_manager.load_personas()}

        self.chats_by_date = {}
        for chat in sorted(all_chats, key=lambda x: x["timestamp"], reverse=True):
            chat_date_str = datetime.fromisoformat(chat["timestamp"]).strftime("%Y-%m-%d")
            if chat_date_str not in self.chats_by_date:
                self.chats_by_date[chat_date_str] = []
            self.chats_by_date[chat_date_str].append(chat)

        if not self.chats_by_date:
            self.chats_list_container.controls.append(
                ft.Text(
                    "No chats saved yet. Start a conversation and save it!",
                    text_align=ft.TextAlign.CENTER,
                    size=16,
                    color=ft.Colors.OUTLINE,
                )
            )
        else:
            for date, chats_on_date in self.chats_by_date.items():
                chat_items = []
                for chat in chats_on_date:
                    persona_info = all_personas.get(chat["persona_id"], {})
                    chat_items.append(
                        ft.ListTile(
                            leading=ft.Image(
                                src=persona_info.get("image_path"),
                                fit=ft.ImageFit.COVER,
                                width=40,
                                height=40,
                                border_radius=20,
                                error_content=ft.Icon(ft.Icons.PERSON),
                            ),
                            title=ft.Text(chat.get("title", "Untitled Chat")),
                            subtitle=ft.Text(
                                f"{len(chat['messages'])} messages with {persona_info.get('name', 'Unknown Persona')}"
                            ),
                            on_click=lambda _, c=chat: self.on_chat_select(c),
                            trailing=ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_ACCENT,
                                on_click=lambda _,
                                c=chat: self._show_delete_confirmation(c["chat_id"], c.get("title", "...")),
                            ),
                            data=chat,
                        )
                    )

                panel = ft.ExpansionPanel(
                    header=ft.ListTile(
                        title=ft.Text(self._format_date(date), weight=ft.FontWeight.BOLD),
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    content=ft.Column(controls=chat_items, spacing=5),
                    expanded=True,
                    can_tap_header=True,
                )

                panel_list = ft.ExpansionPanelList(
                    controls=[panel], 
                    spacing=5,
                    expanded_header_padding=5,
                    elevation=3,
                    divider_color=ft.Colors.GREY,
                )

                self.chats_list_container.controls.append(panel_list)

    def _format_date(self, date_str: str) -> str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if date_obj.date() == datetime.today().date():
            return "Today"
        return date_obj.strftime("%A, %B %d, %Y")
