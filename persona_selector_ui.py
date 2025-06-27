import os
import shutil
import json
import uuid
import flet as ft


class PersonaManager:
    """Handles data and file operations for personas. (No changes needed here)"""

    def __init__(self, file_path="personas.json", assets_dir="assets"):
        self.file_path = file_path
        self.assets_dir = assets_dir
        os.makedirs(self.assets_dir, exist_ok=True)
        if not os.path.isfile(self.file_path):
            self._save_personas_to_disk([])

    def _save_personas_to_disk(self, personas_list):
        with open(self.file_path, "w", encoding="utf8") as f:
            json.dump(personas_list, f, ensure_ascii=False, indent=2)

    def _copy_image_to_assets(self, temp_image_path: str) -> str:
        if not temp_image_path or not os.path.exists(temp_image_path):
            return ""

        filename = os.path.basename(temp_image_path)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
        dest_path = os.path.join(self.assets_dir, unique_filename)
        shutil.copy(temp_image_path, dest_path)
        return dest_path

    def _delete_asset_image(self, image_path: str):
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError as e:
                print(f"Error deleting image {image_path}: {e}")

    def load_personas(self) -> list:
        return json.load(open(self.file_path, encoding="utf8"))

    def add_persona(self, name: str, prompt: str, temp_image_path: str):
        personas = self.load_personas()
        final_image_path = self._copy_image_to_assets(temp_image_path)
        personas.append(
            {
                "id": uuid.uuid4().hex,
                "name": name,
                "prompt": prompt,
                "image_path": final_image_path,
            }
        )
        self._save_personas_to_disk(personas)

    def update_persona(
        self, persona_id: str, name: str, prompt: str, temp_image_path: str | None
    ):
        personas = self.load_personas()
        for i, p in enumerate(personas):
            if p["id"] == persona_id:
                final_image_path = p.get("image_path")
                if temp_image_path:
                    self._delete_asset_image(p.get("image_path"))
                    final_image_path = self._copy_image_to_assets(temp_image_path)

                personas[i] = {
                    "id": persona_id,
                    "name": name,
                    "prompt": prompt,
                    "image_path": final_image_path,
                }
                break

        self._save_personas_to_disk(personas)

    def delete_persona(self, persona_id: str):
        personas = self.load_personas()
        personas_to_keep = [p for p in personas if p["id"] != persona_id]
        for p in personas:
            if p["id"] == persona_id:
                self._delete_asset_image(p.get("image_path"))
                break
        self._save_personas_to_disk(personas_to_keep)


class PersonaSelectorComponent:
    """A reusable component for managing and selecting LLM Personas."""

    def __init__(self, page: ft.Page, on_select: callable = None):
        self.page = page
        self.on_select = on_select
        self.manager = PersonaManager()

        self._add_temp_image_path = None

        self.grid = ft.GridView(
            runs_count=4, 
            spacing=10, 
            run_spacing=10, 
            child_aspect_ratio=1,
            expand=True, 
            padding=10,
        )

        self.add_file_picker = ft.FilePicker(on_result=self._on_add_file_chosen)
        self.page.overlay.append(self.add_file_picker)

        self.add_name_field = ft.TextField(label="Persona Name")
        self.add_prompt_field = ft.TextField(
            label="System Prompt", multiline=True, min_lines=2, max_lines=7
        )
        self.add_image_preview = ft.Container(
            content=ft.Text("No image selected."),
            alignment=ft.alignment.center,
            height=150,
        )
        self.add_dialog = self._create_add_dialog()
        self.page.overlay.append(self.add_dialog)

        self._root = ft.Column(
            [
                self.grid
            ], 
            expand=True, 
            alignment=ft.CrossAxisAlignment.CENTER
        )
        self.update_grid()

    @property
    def view(self) -> ft.Control:
        return self._root

    def update_grid(self):
        self.grid.controls.clear()

        for persona in self.manager.load_personas():
            self.grid.controls.append(self._create_persona_card(persona))

        add_card = ft.Card(
            content=ft.Container(
                content=ft.Icon(name=ft.Icons.ADD, size=58),
                alignment=ft.alignment.center,
                aspect_ratio=1,
                on_click=self._show_add_dialog,
                border=ft.border.all(0.3, ft.Colors.OUTLINE),
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                border_radius=10,
            )
        )

        self.grid.controls.append(add_card)
        if self._root.page:
            self._root.page.update()

    def _handle_card_click(self, persona: dict):
        print(f"Card clicked. Persona ID: {persona['id']}")
        if self.on_select:
            self.on_select(persona)

    def _create_persona_card(self, persona: dict) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                on_click=lambda _, p=persona: self._handle_card_click(p),
                padding=ft.Padding(left=10, top=0, right=10, bottom=10),
                aspect_ratio=1,
                border=ft.border.all(0.3, ft.Colors.OUTLINE),
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.ON_SURFACE),
                border_radius=10,
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        icon_color=ft.Colors.BLUE_ACCENT,
                                        tooltip="Edit",
                                        on_click=lambda _,
                                        p=persona: self._show_edit_dialog(p),
                                        icon_size=20,
                                        padding=0,
                                        visual_density=ft.VisualDensity.COMPACT
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED_ACCENT,
                                        tooltip="Delete",
                                        on_click=lambda _,
                                        p=persona: self._show_delete_dialog(p),
                                        icon_size=20,
                                        padding=0,
                                        visual_density=ft.VisualDensity.COMPACT
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                            margin=ft.margin.only(top=5, bottom=-5),
                        ),
                        ft.Text(
                            persona.get("name", "No Name"),
                            weight=ft.FontWeight.BOLD,
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Image(
                            src=persona.get("image_path"),
                            fit=ft.ImageFit.CONTAIN,
                            expand=True,
                            error_content=ft.Icon(ft.Icons.BROKEN_IMAGE),
                        ),
                        ft.Text(
                            persona.get("prompt", "No prompt"),
                            size=12,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
            )
        )

    def _on_add_file_chosen(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._add_temp_image_path = e.files[0].path
            self.add_image_preview.content = ft.Image(
                src=self._add_temp_image_path, fit=ft.ImageFit.CONTAIN
            )
            self.add_dialog.content.update()

    def _create_add_dialog(self) -> ft.AlertDialog:
        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Persona"),
            content=ft.Column(
                [
                    self.add_name_field,
                    self.add_prompt_field,
                    self.add_image_preview,
                    ft.ElevatedButton(
                        "Select Image",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: self.add_file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["png", "jpg", "jpeg"],
                        ),
                    ),
                ],
                tight=True,
                width=500,
                scroll=ft.ScrollMode.ADAPTIVE,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            actions=[
                ft.TextButton(
                    "Save", on_click=self._save_new_persona,
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
                ft.TextButton(
                    "Cancel", on_click=lambda e: self._close_dialog(self.add_dialog),
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _show_add_dialog(self, e):
        self.add_name_field.value = ""
        self.add_prompt_field.value = ""
        self.add_image_preview.content = ft.Text("No image selected.")
        self._add_temp_image_path = None
        self.add_dialog.open = True
        self.page.update()

    def _save_new_persona(self, e):
        name = self.add_name_field.value.strip()
        prompt = self.add_prompt_field.value.strip()
        if not name or not prompt or not self._add_temp_image_path:
            print("Validation failed: Please fill all fields and select an image.")
            self.page.update()
            return

        self.manager.add_persona(name, prompt, self._add_temp_image_path)
        self._close_dialog(self.add_dialog)
        self.update_grid()

    def _show_edit_dialog(self, persona: dict):
        edit_temp_image_path = [None]

        name_field = ft.TextField(label="Persona Name", value=persona.get("name"))
        prompt_field = ft.TextField(
            label="System Prompt",
            value=persona.get("prompt"),
            multiline=True,
            min_lines=2,
            max_lines=7
        )
        image_preview = ft.Container(
            content=ft.Image(src=persona.get("image_path"), fit=ft.ImageFit.CONTAIN)
            if persona.get("image_path")
            else ft.Text("No image."),
            height=150,
            alignment=ft.alignment.center,
        )

        def on_edit_file_chosen(e: ft.FilePickerResultEvent):
            if e.files:
                edit_temp_image_path[0] = e.files[0].path
                image_preview.content = ft.Image(
                    src=edit_temp_image_path[0], fit=ft.ImageFit.CONTAIN
                )
                edit_dialog.content.update()

        edit_file_picker = ft.FilePicker(on_result=on_edit_file_chosen)
        self.page.overlay.append(edit_file_picker)

        def save_changes(e):
            self.manager.update_persona(
                persona_id=persona["id"],
                name=name_field.value.strip(),
                prompt=prompt_field.value.strip(),
                temp_image_path=edit_temp_image_path[0],
            )
            self._close_dialog(edit_dialog)
            self.page.overlay.remove(edit_file_picker)
            self.update_grid()

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {persona.get('name')}"),
            content=ft.Column(
                [
                    name_field,
                    prompt_field,
                    image_preview,
                    ft.ElevatedButton(
                        "Change Image",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _: edit_file_picker.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["png", "jpg", "jpeg"],
                        ),
                    ),
                ],
                tight=True,
                width=500,
                scroll=ft.ScrollMode.ADAPTIVE,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            actions=[
                ft.TextButton(
                    "Save", on_click=save_changes,
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
                ft.TextButton(
                    "Cancel", on_click=lambda e: self._close_dialog(edit_dialog),
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
            ],
        )
        self.page.overlay.append(edit_dialog)
        edit_dialog.open = True
        self.page.update()

    def _show_delete_dialog(self, persona: dict):
        def confirm_delete(e):
            self.manager.delete_persona(persona["id"])
            self._close_dialog(delete_dialog)
            self.update_grid()

        delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Markdown(
                f"Are you sure you want to delete '**{persona.get('name')}**'?"
            ),
            actions=[
                ft.TextButton(
                    "Delete", on_click=confirm_delete,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED,
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
                ft.TextButton(
                    "Cancel", on_click=lambda e: self._close_dialog(delete_dialog),
                    style=ft.ButtonStyle(
                        padding=15,
                        text_style=ft.TextStyle(size=17, weight=ft.FontWeight.W_500)
                    )
                ),
            ],
        )
        self.page.overlay.append(delete_dialog)
        delete_dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog):
        dialog.open = False
        self.page.update()
