import flet as ft
from gguf_chat_ui import GGUFChatApp
from persona_selector_ui import PersonaSelectorComponent, PersonaManager

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    persona_selector_component = [None]
    chat_app_component = [None]
    persona_to_load_in_chat = [None] 
    menu_expanded = [False]

    content_area = ft.Container(expand=True)
    persona_manager = PersonaManager()

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
            persona = persona_to_load_in_chat[0]
            persona_to_load_in_chat[0] = None

            if chat_app_component[0] is not None and persona:
                chat_app_component[0].start_new_chat(persona)

            elif chat_app_component[0] is None:
                if not persona:
                    all_personas = persona_manager.load_personas()
                    persona = all_personas[0] if all_personas else None
                
                if persona:
                    chat_app_component[0] = GGUFChatApp(page, persona=persona)
                else:
                    chat_app_component[0] = ft.Column([
                        ft.Icon(ft.Icons.PERSON_SEARCH, size=50, color=ft.Colors.OUTLINE),
                        ft.Text("No personas found.", size=16),
                        ft.Text("Go to 'Bots' to create one.", color=ft.Colors.OUTLINE)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            
            content_area.content = chat_app_component[0].view if isinstance(chat_app_component[0], GGUFChatApp) else chat_app_component[0]

            if isinstance(chat_app_component[0], GGUFChatApp):
                chat_app_component[0]._on_resize()

        elif index == 3:
            content_area.content = ft.Text("Memories", size=20)
        elif index == 4:
            content_area.content = ft.Text("Chats", size=20)
        elif index == 5:
            content_area.content = ft.Text("Settings", size=20)
        
        page.update()

    def on_persona_selected(persona: dict):
        persona_to_load_in_chat[0] = persona
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
