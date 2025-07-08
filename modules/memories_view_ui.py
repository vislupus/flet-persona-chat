import flet as ft
from modules.history_manager import HistoryManager
from modules.persona_selector_ui import PersonaManager
from datetime import datetime


class MemoriesViewComponent:
    def __init__(self, page: ft.Page, on_go_to_chat: callable):
        self.page = page
        self.on_go_to_chat = on_go_to_chat
        self.history_manager = HistoryManager()
        self.persona_manager = PersonaManager()

        self.memories_list = ft.ListView(
            expand=True, 
            spacing=15, 
            padding=0,
        )

        self._root = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER_SPECIAL, size=28),
                            ft.Text("Memories", theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.only(left=10, right=10, top=15, bottom=10),
                ),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.memories_list,
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
        )

    @property
    def view(self) -> ft.Control:
        return self._root

    def _show_delete_confirmation(self, memory_id: str):
        def confirm_delete(e):
            self.history_manager.delete_memory(memory_id)
            self.update_view()
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Delete this memory?"),
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
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def update_view(self):
        self.memories_list.controls.clear()
        all_memories = self.history_manager.load_memories()
        all_personas = {p["id"]: p for p in self.persona_manager.load_personas()}

        all_chats = self.history_manager.load_chats()
        saved_chat_ids = {c.get("chat_id") for c in all_chats}

        if not all_memories:
            self.memories_list.controls.append(
                ft.Text(
                    "No memories saved yet.",
                    text_align=ft.TextAlign.CENTER,
                    size=16,
                    color=ft.Colors.OUTLINE,
                )
            )
        else:
            for memory in sorted(all_memories, key=lambda x: x["timestamp"], reverse=True):
                persona_info = all_personas.get(memory["persona_id"], {})

                actions_row = ft.Row(alignment=ft.MainAxisAlignment.END)

                chat_id_from_memory = memory.get("chat_id")
                if chat_id_from_memory and chat_id_from_memory in saved_chat_ids:
                    actions_row.controls.append(
                        ft.TextButton(
                            "Go to Chat",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda _,
                            cid=chat_id_from_memory: self.on_go_to_chat(cid),
                        )
                    )

                actions_row.controls.append(
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_ACCENT,
                        on_click=lambda _, m=memory: self._show_delete_confirmation(m["memory_id"]),
                    )
                )

                memory_card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Image(
                                        src=persona_info.get("image_path"),
                                        width=40,
                                        height=40,
                                        fit=ft.ImageFit.COVER,
                                        border_radius=20,
                                    ),
                                    title=ft.Text(
                                        f"Memory with {persona_info.get('name', 'Unknown')}"
                                    ),
                                    subtitle=ft.Text(
                                        datetime.fromisoformat(
                                            memory["timestamp"]
                                        ).strftime("%Y-%m-%d %H:%M")
                                    ),
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f'"{memory["summary"]}"', italic=True
                                    ),
                                ),
                                actions_row,
                            ]
                        ),
                    )
                )
                self.memories_list.controls.append(memory_card)

        if self.page:
            self.page.update()
