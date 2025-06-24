import flet as ft
from gguf_chat_ui import GGUFChatApp

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    chat_app = [None]
    menu_expanded = [False]

    content_area = ft.Container(expand=True)

    def toggle_menu(e):
        menu_expanded[0] = not menu_expanded[0]
        navigation_rail.extended = menu_expanded[0]
        page.update()

    def change_content(e):
        index = e.control.selected_index
        if index == 0:
            content_area.content = ft.Text("Home", size=20)
        elif index == 1:
            content_area.content = ft.Text("Bots", size=20)
        elif index == 2:
            if chat_app[0] is None:
                chat_app[0] = GGUFChatApp(page, mount_to=content_area)
            else:
                content_area.content = chat_app[0].view

            chat_app[0]._on_resize(page)
        elif index == 3:
            content_area.content = ft.Text("Memories", size=20)
        elif index == 4:
            content_area.content = ft.Text("Chats", size=20)
        elif index == 5:
            content_area.content = ft.Text("Settings", size=20)
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
        on_change=change_content,
        destinations=[
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.HOME_OUTLINED, "Home"),
                selected_icon=rail_icon(ft.Icons.HOME, "Home"),
                label="Home"
            ),
            ft.NavigationRailDestination(
                icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "Bots"),
                selected_icon=rail_icon(ft.Icons.ACCOUNT_CIRCLE, "Bots"),
                label="Bots",
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

    # chat_app[0] = GGUFChatApp(page, attach_to_page=False)
    # content_area.content = chat_app[0].view
    content_area.content = ft.Text("Home", size=20)
    page.update()

    def update_menu_spacer(e):
        menu_spacer.height = e.height - 48*7 - 10
        menu_spacer.update()

    def handle_resize(e):
        update_menu_spacer(e)

        if chat_app[0]:
            chat_app[0]._on_resize(e)

    page.on_resized = handle_resize
    handle_resize(page) 

ft.app(target=main, assets_dir="assets")
