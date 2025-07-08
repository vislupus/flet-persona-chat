import flet as ft
from datetime import datetime
import json
import os
import uuid

class PersonInfoManager:
    def __init__(self, file_path="person_info.json"):
        self.file_path = f"assets/{file_path}"
        if not os.path.isfile(self.file_path):
            self._write_json([])

    def _write_json(self, data):
        with open(self.file_path, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_info(self) -> list:
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r", encoding="utf8") as f:
                return json.load(f)
        return []

    def add_info(self, content: str):
        info_list = self.load_info()
        new_info = {
            "info_id": uuid.uuid4().hex,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        info_list.append(new_info)
        self._write_json(info_list)
        print(f"Info {new_info['info_id']} saved.")

    def update_info(self, info_id: str, content: str):
        info_list = self.load_info()
        for i, info in enumerate(info_list):
            if info["info_id"] == info_id:
                info_list[i]["content"] = content
                info_list[i]["timestamp"] = datetime.now().isoformat()
                break
        self._write_json(info_list)
        print(f"Info {info_id} updated.")

    def delete_info(self, info_id: str):
        info_list = self.load_info()
        updated_list = [info for info in info_list if info["info_id"] != info_id]
        self._write_json(updated_list)
        print(f"Info {info_id} deleted.")

class PersonViewComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.manager = PersonInfoManager()

        self.info_list = ft.ListView(
            expand=True,
            spacing=5,
        )

        self.add_info_field = ft.TextField(
            label="Enter personal info",
            multiline=True,
            min_lines=2,
            max_lines=5
        )
        self.add_dialog = self._create_add_dialog()
        self.page.overlay.append(self.add_dialog)

        self._root = ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=28),
                                    ft.Text(
                                        "Personal Info",
                                        theme_style=ft.TextThemeStyle.HEADLINE_SMALL
                                    )
                                ],
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.IconButton(
                                ft.Icons.ADD,
                                tooltip="Add Info (Ctrl+N)",
                                on_click=self._show_add_dialog
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center_left,
                    padding=10
                ),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.info_list,
                                padding=ft.padding.only(right=20),
                            ),
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                    ),
                    padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
                    expand=True,
                )
            ],
            expand=True,
            spacing=0
        )

        self.page.on_keyboard_event = self._handle_keyboard_event
        self.update_view()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _handle_keyboard_event(self, e: ft.KeyboardEvent):
        if e.ctrl and e.key.lower() == "n":
            self._show_add_dialog(None)

    def _create_add_dialog(self):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Personal Info"),
            content=ft.Column(
                [self.add_info_field],
                tight=True,
                width=500,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            actions=[
                ft.TextButton(
                    "Save",
                    on_click=self._save_new_info,
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self._close_dialog(self.add_dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def _show_add_dialog(self, e):
        self.add_info_field.value = ""
        self.add_dialog.open = True
        self.page.update()

    def _save_new_info(self, e):
        content = self.add_info_field.value.strip()
        if not content:
            return
        self.manager.add_info(content)
        self._close_dialog(self.add_dialog)
        self.update_view()

    def _show_edit_dialog(self, info: dict):
        edit_info_field = ft.TextField(
            label="Edit personal info",
            value=info["content"],
            multiline=True,
            min_lines=2,
            max_lines=5
        )

        def save_changes(e):
            content = edit_info_field.value.strip()
            if not content:
                return
            self.manager.update_info(info["info_id"], content)
            self._close_dialog(edit_dialog)
            self.update_view()

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Personal Info"),
            content=ft.Column(
                [edit_info_field],
                tight=True,
                width=500,
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            actions=[
                ft.TextButton(
                    "Save",
                    on_click=save_changes,
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: self._close_dialog(edit_dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.overlay.append(edit_dialog)
        edit_dialog.open = True
        self.page.update()

    def _show_delete_confirmation(self, info_id: str):
        def confirm_delete(e):
            self.manager.delete_info(info_id)
            self.update_view()
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Delete this personal info?"),
            actions=[
                ft.TextButton(
                    "Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.Colors.RED)
                ),
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: setattr(dlg, "open", False) or self.page.update()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog):
        dialog.open = False
        self.page.update()

    def _build_info_list_tile(self, info: dict) -> ft.Card:
        actions_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.BLUE_ACCENT,
                    tooltip="Edit",
                    on_click=lambda e, i=info: self._show_edit_dialog(i)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_ACCENT,
                    tooltip="Delete",
                    on_click=lambda e, i=info: self._show_delete_confirmation(i["info_id"])
                )
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Card(
            content=ft.Container(
                padding=0,
                content=ft.ListTile(
                    title=ft.Row(
                        [
                            ft.Text(
                                info["content"],
                                selectable=True,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                expand=True
                            ),
                            actions_row
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    key=info["info_id"]
                )
            )
        )

    def update_view(self):
        self.info_list.controls.clear()
        all_info = self.manager.load_info()

        if not all_info:
            self.info_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No personal info saved yet. Add info with the (+) button.",
                        size=16,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.OUTLINE
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            sorted_info = sorted(all_info, key=lambda x: x["timestamp"], reverse=False)
            for info in sorted_info:
                self.info_list.controls.append(self._build_info_list_tile(info))

        if self.page:
            self.page.update()