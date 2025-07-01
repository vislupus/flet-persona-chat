import flet as ft
from gguf_chat_ui import GGUFChatApp
from persona_selector_ui import PersonaSelectorComponent, PersonaManager
from chats_view_ui import ChatsViewComponent
from memories_view_ui import MemoriesViewComponent
from chatbot import ChatBot

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    persona_selector_component = [None]
    chat_app_component = [None]
    chats_view_component = [None]
    persona_to_load_in_chat = [None]
    chat_to_load = [None]
    menu_expanded = [False]
    memories_view_component = [None]

    content_area = ft.Container(expand=True)
    persona_manager = PersonaManager()

    def get_chat_app_component():
        # Lazy initialization
        if chat_app_component[0] is None:
             # This is a bit complex, we will address it by simplifying the chat app creation
             pass
        return chat_app_component[0]

    def on_chat_selected(chat: dict):
        """Called when a user clicks a saved chat."""
        # Store the chat data that needs to be loaded
        chat_to_load[0] = chat
        # Ensure we are not trying to load a new persona
        persona_to_load_in_chat[0] = None
        
        # Navigate to the chat room
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
             # Get the states
            persona_to_load = persona_to_load_in_chat[0]
            saved_chat_to_load = chat_to_load[0]
            
            # Reset states after reading them
            persona_to_load_in_chat[0] = None
            chat_to_load[0] = None

            # Determine the persona for the chat session
            persona_for_session = None
            if saved_chat_to_load:
                # If loading a saved chat, find its persona
                all_personas = {p['id']: p for p in persona_manager.load_personas()}
                persona_for_session = all_personas.get(saved_chat_to_load['persona_id'])
            elif persona_to_load:
                # If starting a new chat with a selected persona
                persona_for_session = persona_to_load
            elif chat_app_component[0] is None:
                # If opening the chat tab for the first time, get the default persona
                all_personas = persona_manager.load_personas()
                persona_for_session = all_personas[0] if all_personas else None

            if persona_for_session:
                if chat_app_component[0] is None:
                    chat_app_component[0] = GGUFChatApp(page, persona=persona_for_session)
                
                if persona_to_load:
                    chat_app_component[0].start_new_chat(persona_to_load)
                
                elif saved_chat_to_load:
                    chat_app_component[0].start_new_chat(persona_for_session) 
                    chat_app_component[0].load_chat_history(saved_chat_to_load['messages'])

            if chat_app_component[0]:
                content_area.content = chat_app_component[0].view
                chat_app_component[0]._on_resize()
            else:
                content_area.content = ft.Column([ft.Icon(ft.icons.PERSON_SEARCH, size=50), ft.Text("No personas found.")])

        elif index == 3:
            if memories_view_component[0] is None:
                memories_view_component[0] = MemoriesViewComponent(page)
            
            content_area.content = memories_view_component[0].view
            memories_view_component[0].update_view()
        elif index == 4:
            if chats_view_component[0] is None:
                chats_view_component[0] = ChatsViewComponent(page, on_chat_select=on_chat_selected)
            
            # Set the content and tell the component to refresh its data
            content_area.content = chats_view_component[0].view
            chats_view_component[0].update_view()
        elif index == 5:
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
                icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "Personas"),
                selected_icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE, "Personas"),
                label="Personas",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.CHAT_OUTLINED, "Chat room"),
                selected_icon=rail_icon(ft.Icons.CHAT, "Chat room"),
                label="Chat room",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.FOLDER_OUTLINED, "Memories"),
                selected_icon=rail_icon(ft.Icons.FOLDER, "Memories"),
                label="Memories",
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.TEXT_SNIPPET_OUTLINED, "Chats"),
                selected_icon=rail_icon(ft.Icons.TEXT_SNIPPET, "Chats"),
                label="Chats",
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
        menu_spacer.height = e.height - 48*7 - 10
        menu_spacer.update()

        if chat_app_component[0] and navigation_rail.selected_index == 2:
            chat_app_component[0]._on_resize(e)
            page.update()

    page.on_resized = handle_resize
    handle_resize(page)

ft.app(target=main, assets_dir="assets")
