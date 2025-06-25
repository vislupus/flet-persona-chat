import os
import shutil
import json
import uuid
import flet as ft


CHAR_FILE   = "characters.json"
ASSETS_DIR  = "assets"

characters = []


os.makedirs(ASSETS_DIR, exist_ok=True)
if not os.path.isfile(CHAR_FILE):
    with open(CHAR_FILE, "w", encoding="utf8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)



def load_chars() -> list:
    with open(CHAR_FILE, encoding="utf8") as f:
        return json.load(f)

def save_chars(characters):
    with open(CHAR_FILE, "w", encoding="utf8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)



def main(page: ft.Page):
    page.title = "Герои"
    page.padding = 20

    grid = ft.GridView(
        runs_count=4,
        spacing=10,
        run_spacing=10,
        expand=True,
    )

    characters: list[dict] = load_chars()

    name_field = ft.TextField(label="Име на героя")
    prompt_field = ft.TextField(label="Prompt на героя")
    image_display = ft.Container(content=ft.Text("Няма избрано изображение"))
    selected_image_path = {"path": None}

    def on_file_chosen(e: ft.FilePickerResultEvent):
        if e.files:
            src_path = e.files[0].path
            # ext = os.path.splitext(src_path)[1].lower()
            # new_name = f"{uuid.uuid4().hex}{ext}"
            dst_path = os.path.join(ASSETS_DIR, e.files[0].name)

            shutil.copy(src_path, dst_path)

            selected_image_path["path"] = dst_path

            image_display.content = ft.Image(src=dst_path, fit=ft.ImageFit.CONTAIN)
            image_display.width = 200
            image_display.height = 200
            page.update()

    pick_files_dialog = ft.FilePicker(on_result=on_file_chosen)
    page.overlay.append(pick_files_dialog)

    def add_bot():
        grid.controls.clear()

        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color=ft.Colors.BLUE,
            tooltip="Edit",
            icon_size=24,
            # on_click=show_edit_dialog,
            style=ft.ButtonStyle(padding=0),
        )

        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Delete",
            icon_size=24,
            # on_click=lambda e, pid=p["id"], pname=p["name"]: show_delete_dialog(e, pid, pname),
            style=ft.ButtonStyle(padding=0),
        )

        for ch in characters:
            grid.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            edit_button,
                                            delete_button
                                        ], 
                                        spacing=0,
                                        alignment=ft.MainAxisAlignment.END,
                                        vertical_alignment=ft.CrossAxisAlignment.START
                                    ),
                                    padding=0,
                                    margin=ft.margin.only(bottom=0, top=-5),
                                ),
                                ft.Text(ch.get("name", "name"), weight=ft.FontWeight.BOLD, size=16),
                                ft.Image(src=ch["img"], fit=ft.ImageFit.CONTAIN, expand=True),
                                ft.Text(ch.get("prompt", "prompt"), size=12, max_lines=5, overflow=ft.TextOverflow.ELLIPSIS)
                            ],
                            tight=True,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        padding=10,
                        aspect_ratio=1,
                        alignment=ft.alignment.center,
                    )
                )
            )

        grid.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Icon(name=ft.Icons.ADD, size=48),
                    alignment=ft.alignment.center,
                    aspect_ratio=1,
                    on_click=open_dialog,
                ),
            )
        )

        page.update()

    def save_character(e):
        name = name_field.value.strip()
        prompt = prompt_field.value.strip()
        img = selected_image_path.get("path")

        if not name or not prompt or not img:
            page.snack_bar = ft.SnackBar(ft.Text("Попълнете всички полета и изберете изображение!"))
            page.snack_bar.open = True
            page.update()
            return

        characters.append({
            "id": uuid.uuid4().hex,
            "name": name,
            "prompt": prompt,
            "img": img
        })

        save_chars(characters)

        dialog.open = False
        name_field.value = ""
        prompt_field.value = ""
        selected_image_path["path"] = None
        image_display.content = ft.Text("Няма избрано изображение")
        image_display.width = None
        image_display.height = None

        add_bot()
        page.update()



    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Add new persona"),
        content=ft.Column([
            name_field,
            prompt_field,
            image_display,
            ft.ElevatedButton(
                "Избери изображение",
                icon=ft.Icons.UPLOAD_FILE,
                style=ft.ButtonStyle(
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    shape=ft.ContinuousRectangleBorder(radius=30)
                ),
                on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["png", "jpg", "jpeg"],
                            dialog_title="Изберете картинка за героя",
                ),
            ),
        ], tight=True),
        actions=[
            ft.TextButton("OK", on_click=save_character),
            ft.TextButton("Отказ", on_click=lambda e: close_dialog())
        ],
    )

    def open_dialog(e):
        dialog.open = True
        page.overlay.append(dialog)
        page.update()

    def close_dialog():
        dialog.open = False
        page.update()


    add_bot()

    page.add(
        ft.Column([
            grid
        ])
    )

ft.app(target=main)
