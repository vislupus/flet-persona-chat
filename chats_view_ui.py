import flet as ft
from history_manager import HistoryManager
from persona_selector_ui import PersonaManager
from datetime import datetime

class ChatsViewComponent:
    def __init__(self, page: ft.Page, on_chat_select: callable):
        self.page = page
        self.on_chat_select = on_chat_select # Callback to tell the main app which chat to load
        self.history_manager = HistoryManager()
        self.persona_manager = PersonaManager()

        self.chats_by_date = {}
        self.chats_list_container = ft.Column(expand=True, spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        
        self._root = ft.Column([
            ft.Row([ft.Icon(ft.Icons.HISTORY), ft.Text("Saved Chats", style=ft.TextThemeStyle.HEADLINE_MEDIUM)]),
            ft.Divider(),
            self.chats_list_container
        ], expand=True)

    @property
    def view(self) -> ft.Control:
        return self._root

    def update_view(self):
        """Loads all chats and rebuilds the view, grouping them by date."""
        self.chats_list_container.controls.clear()
        all_chats = self.history_manager.load_chats()
        all_personas = {p['id']: p for p in self.persona_manager.load_personas()}

        self.chats_by_date = {}
        for chat in sorted(all_chats, key=lambda x: x['timestamp'], reverse=True):
            chat_date_str = datetime.fromisoformat(chat['timestamp']).strftime('%Y-%m-%d')
            if chat_date_str not in self.chats_by_date:
                self.chats_by_date[chat_date_str] = []
            self.chats_by_date[chat_date_str].append(chat)

        if not self.chats_by_date:
            self.chats_list_container.controls.append(
                ft.Text("No chats saved yet. Start a conversation and save it!", text_align=ft.TextAlign.CENTER, size=16, color=ft.Colors.OUTLINE)
            )
        else:
            for date, chats_on_date in self.chats_by_date.items():
                chat_items = []
                for chat in chats_on_date:
                    persona_info = all_personas.get(chat['persona_id'], {})
                    chat_items.append(
                        ft.ListTile(
                            leading=ft.Image(src=persona_info.get('image_path'), width=40, height=40, fit=ft.ImageFit.COVER, border_radius=20, error_content=ft.Icon(ft.Icons.PERSON)),
                            title=ft.Text(chat.get('title', 'Untitled Chat')),
                            subtitle=ft.Text(f"{len(chat['messages'])} messages with {persona_info.get('name', 'Unknown Persona')}"),
                            on_click=lambda _, c=chat: self.on_chat_select(c),
                            data=chat
                        )
                    )

                panel = ft.ExpansionPanel(
                    header=ft.ListTile(title=ft.Text(self._format_date(date), weight=ft.FontWeight.BOLD)),
                    content=ft.Column(controls=chat_items),
                    expanded=True 
                )
                
                panel_list = ft.ExpansionPanelList(controls=[panel])
                
                self.chats_list_container.controls.append(panel_list)


    def _format_date(self, date_str: str) -> str:
        """Formats the date string for display."""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        if date_obj.date() == datetime.today().date():
            return "Today"
        return date_obj.strftime('%A, %B %d, %Y')