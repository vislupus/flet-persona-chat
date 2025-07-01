import flet as ft
from history_manager import HistoryManager
from persona_selector_ui import PersonaManager
from datetime import datetime

class MemoriesViewComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.history_manager = HistoryManager()
        self.persona_manager = PersonaManager()

        self.memories_list = ft.ListView(expand=True, spacing=15, padding=20)
        
        self._root = ft.Column([
            ft.Row([ft.Icon(ft.Icons.FOLDER_SPECIAL), ft.Text("Memories", style=ft.TextThemeStyle.HEADLINE_MEDIUM)]),
            ft.Divider(),
            self.memories_list
        ], expand=True)

    @property
    def view(self) -> ft.Control:
        return self._root

    def update_view(self):
        """Loads all memories and rebuilds the view."""
        self.memories_list.controls.clear()
        all_memories = self.history_manager.load_memories()
        all_personas = {p['id']: p for p in self.persona_manager.load_personas()}

        if not all_memories:
            self.memories_list.controls.append(
                ft.Text("No memories saved yet.", text_align=ft.TextAlign.CENTER, size=16, color=ft.Colors.OUTLINE)
            )
        else:
            for memory in sorted(all_memories, key=lambda x: x['timestamp'], reverse=True):
                persona_info = all_personas.get(memory['persona_id'], {})
                memory_card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Image(src=persona_info.get('image_path'), width=40, height=40, fit=ft.ImageFit.COVER, border_radius=20),
                                title=ft.Text(f"Memory with {persona_info.get('name', 'Unknown')}"),
                                subtitle=ft.Text(datetime.fromisoformat(memory['timestamp']).strftime('%Y-%m-%d %H:%M'))
                            ),
                            ft.Container(
                                content=ft.Text(f"\"{memory['summary']}\"", italic=True),
                                padding=ft.padding.only(top=10, left=15, right=15, bottom=5)
                            )
                        ])
                    )
                )
                self.memories_list.controls.append(memory_card)
        
        if self.page:
            self.page.update()