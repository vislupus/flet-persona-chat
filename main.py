import flet as ft
from gguf_chat_ui import GGUFChatApp
from persona_selector_ui import PersonaSelectorComponent, PersonaManager
from chats_view_ui import ChatsViewComponent
from memories_view_ui import MemoriesViewComponent
from history_manager import HistoryManager
from person_view_ui import PersonViewComponent


def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    persona_selector_component = [None]
    chat_app_component = [None]
    chats_view_component = [None]
    memories_view_component = [None]
    persona_to_load_in_chat = [None]
    chat_to_load = [None]
    menu_expanded = [False]
    person_view_component = [None]

    content_area = ft.Container(expand=True)
    persona_manager = PersonaManager()

    def _show_info_dialog(title: str, content: str):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[ft.TextButton("OK", on_click=lambda e: setattr(dlg, 'open', False) or page.update())]
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def on_go_to_chat(chat_id: str):
        chats = HistoryManager().load_chats()
        target_chat = next((c for c in chats if c.get('chat_id') == chat_id), None)
        if target_chat:
            on_chat_selected(target_chat)
        else:
            _show_info_dialog("Error", f"Could not find associated chat (ID: {chat_id[:8]}...). It may have been deleted.")
            page.update()


    def on_chat_selected(chat: dict):
        """Called when a user clicks a saved chat."""
        chat_to_load[0] = chat
        persona_to_load_in_chat[0] = None
        
        navigation_rail.selected_index = 2
        update_main_view()

    def update_main_view():
        index = navigation_rail.selected_index

        if index == 0: # Home
            content_area.content = ft.Text("Home View", size=30)

        elif index == 1: # Personas
            if persona_selector_component[0] is None:
                persona_selector_component[0] = PersonaSelectorComponent(page, on_select=on_persona_selected)
            content_area.content = persona_selector_component[0].view
            persona_selector_component[0].update_grid()

        elif index == 2: # Chat room
            persona_to_load = persona_to_load_in_chat[0]
            saved_chat_to_load = chat_to_load[0]
            
            # Consume the state after reading it
            persona_to_load_in_chat[0] = None
            chat_to_load[0] = None

            persona_for_session = None
            if saved_chat_to_load:
                # Load all personas and create a lookup dictionary
                all_personas = {p['id']: p for p in persona_manager.load_personas()}
                persona_for_session = all_personas.get(saved_chat_to_load['persona_id'])
            elif persona_to_load:
                persona_for_session = persona_to_load
            elif chat_app_component[0] is None: # If opening chat tab directly for the first time
                all_personas = persona_manager.load_personas()
                persona_for_session = all_personas[0] if all_personas else None

            # Create chat component if it doesn't exist AND we have a persona to show
            if chat_app_component[0] is None and persona_for_session:
                chat_app_component[0] = GGUFChatApp(page, persona=persona_for_session)
            
            # Now, update the component if it exists
            if chat_app_component[0]:
                if persona_to_load: # New chat from persona selection
                    chat_app_component[0].start_new_chat(persona_to_load)
                elif saved_chat_to_load and persona_for_session: # Loading a saved chat
                    # We need to switch the persona first, then load history
                    chat_app_component[0].start_new_chat(persona_for_session) 
                    chat_app_component[0].load_chat_history(saved_chat_to_load)

                content_area.content = chat_app_component[0].view
                chat_app_component[0]._on_resize()
            else:
                # Fallback if no persona is available at all
                content_area.content = ft.Column([
                    ft.Icon(ft.Icons.PERSON_SEARCH, size=50),
                    ft.Text("No personas found. Please create one in the 'Personas' tab.")
                ])

        elif index == 3: # Memories
            if memories_view_component[0] is None:
                memories_view_component[0] = MemoriesViewComponent(page, on_go_to_chat=on_go_to_chat)
            
            content_area.content = memories_view_component[0].view
            memories_view_component[0].update_view()
        elif index == 4: # Chats
            if chats_view_component[0] is None:
                chats_view_component[0] = ChatsViewComponent(page, on_chat_select=on_chat_selected)
            
            content_area.content = chats_view_component[0].view
            chats_view_component[0].update_view()
        elif index == 5: # Person
            if person_view_component[0] is None:
                person_view_component[0] = PersonViewComponent(page)
            content_area.content = person_view_component[0].view
            person_view_component[0].update_view()
        elif index == 6: # Settings
            content_area.content = ft.Text("Settings", size=20)
        
        page.update()

    def on_persona_selected(persona: dict):
        persona_to_load_in_chat[0] = persona
        chat_to_load[0] = None
        navigation_rail.selected_index = 2
        update_main_view()

    def handle_navigation_change(e: ft.ControlEvent):
        """Called ONLY when the user clicks on the navigation rail."""
        update_main_view()

    def toggle_menu(e):
        menu_expanded[0] = not menu_expanded[0]
        navigation_rail.extended = menu_expanded[0]
        page.update()


    def rail_icon(icon_name: str, msg: str):
        return ft.Icon(icon_name, size=24, tooltip=msg)

    menu_spacer = ft.Container(height=0)

    navigation_rail = ft.NavigationRail(
        selected_index=0,
        # label_type=ft.NavigationRailLabelType.ALL,
        # label_type=ft.NavigationRailLabelType.SELECTED,
        label_type=ft.NavigationRailLabelType.NONE,
        # width=70,
        min_width=70,
        extended=False,
        min_extended_width=150,
        # group_alignment=-0.9,
        # group_alignment=1.0,
        elevation=1,
        indicator_shape=ft.RoundedRectangleBorder(radius=5),
        trailing=ft.Column(
            [
                menu_spacer,
                ft.Container(
                    content=ft.IconButton(ft.Icons.MENU, on_click=toggle_menu),
                ),
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_change=handle_navigation_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.HOME_OUTLINED, "Home"),
                selected_icon=rail_icon(ft.Icons.HOME, "Home"),
                label="Home"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.PEOPLE_OUTLINED, "Personas"),
                selected_icon=rail_icon(ft.Icons.PEOPLE, "Personas"),
                label="Personas",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.CHAT_OUTLINED, "Chat room"),
                selected_icon=rail_icon(ft.Icons.CHAT, "Chat room"),
                label="Chat room",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.WEB_STORIES_OUTLINED, "Memories"),
                selected_icon=rail_icon(ft.Icons.WEB_STORIES, "Memories"),
                label="Memories",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.TEXT_SNIPPET_OUTLINED, "Chats"),
                selected_icon=rail_icon(ft.Icons.TEXT_SNIPPET, "Chats"),
                label="Chats",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "Person"),
                selected_icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE, "Person"),
                label="Person",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.SETTINGS_OUTLINED, "Settings"),
                selected_icon=rail_icon(ft.Icons.SETTINGS, "Settings"),
                label="Settings",
            ),
        ],
    )

    page.add(
        ft.Row(
            controls=[navigation_rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
            spacing=0,
        )
    )

    content_area.content = ft.Text("Home", size=20)
    page.update()

    def handle_resize(e):
        menu_spacer.height = e.height - 48*8 - 10
        menu_spacer.update()

        if chat_app_component[0] and navigation_rail.selected_index == 2:
            chat_app_component[0]._on_resize(e)
            page.update()

    page.on_resized = handle_resize
    handle_resize(page)

ft.app(target=main, assets_dir="assets")
