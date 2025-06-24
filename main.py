import flet as ft
from gguf_chat_ui import GGUFChatApp

def main(page: ft.Page):
    page.title = "GGUF ChatBot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    GGUFChatApp(page)

ft.app(target=main, assets_dir="assets")
