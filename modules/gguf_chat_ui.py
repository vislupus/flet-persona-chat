import asyncio
import threading
from time import time
import uuid
import flet as ft
from modules.chatbot import ChatBot
from modules.history_manager import HistoryManager


class GGUFChatApp:

    BUBBLE_RATIO = 0.7
    LOADING_BUBBLE_WIDTH = 80

    def __init__(self, page: ft.Page, persona: dict):
        self.page = page
        self.current_persona = persona
        self._bot = {"instance": None}
        self.history_manager = HistoryManager()
        
        self.current_chat_messages = []
        self.current_chat_id = None
        self.editing_message_id = None
        self.active_bot_bubble = None
        self.active_bot_wrapper = None
        self.active_loading_row = None

        self.persona_avatar = ft.Container(
            content=ft.Image(
                src=self.current_persona.get("image_path"),
                fit=ft.ImageFit.COVER,
                error_content=ft.Icon(ft.Icons.PERSON)
            ),
            width=45,
            height=45,
            border_radius=23,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_200),
            border=ft.border.all(0.3, ft.Colors.OUTLINE),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
        )
        self.persona_name = ft.Text(
            self.current_persona.get("name", "Unknown"), 
            size=18, 
            weight=ft.FontWeight.BOLD
        )

        self.chat_actions_menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(icon=ft.Icons.SAVE_ALT, text="Save Chat", on_click=self._save_chat_click),
                ft.PopupMenuItem(icon=ft.Icons.BOOKMARK_ADD, text="Save as Memory", on_click=self._save_memory_click),
                ft.PopupMenuItem(),  # Divider
                ft.PopupMenuItem(icon=ft.Icons.ADD_COMMENT_ROUNDED, text="New Chat", on_click=self._new_chat_click),
            ]
        )
        
        self.header_container = ft.Container(
            content=ft.ListTile(
                leading=self.persona_avatar,
                title=self.persona_name,
                subtitle=ft.Text("LLM Chat", size=12),
                trailing=self.chat_actions_menu
            ),
            padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            height=70
        )

        self.user_input = ft.TextField(
            label="Enter your message", expand=True,
            on_submit=self._send_message, border_radius=10
        )

        self.send_btn = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED, tooltip="Send Message",
            on_click=self._send_message
        )

        self.cancel_btn = ft.IconButton(
            icon=ft.Icons.CANCEL, tooltip="Cancel Edit",
            on_click=self._cancel_edit,
            visible=False
        )

        self.chat_column = ft.Column(
            expand=True, 
            spacing=10, 
            scroll=ft.ScrollMode.ALWAYS,
            auto_scroll=False,
        )

        self.chat_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=self.chat_column,
                        padding=ft.padding.only(right=10),
                        expand=True,
                    )
                ],
            ),
            expand=True,
            padding=ft.padding.only(left=20, top=10, bottom=10),
            bgcolor=ft.Colors.BLUE_50,
            width=float("inf"),
        )

        self.input_container = ft.Container(
            content=ft.Row([self.user_input, self.send_btn, self.cancel_btn]),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            height=80,
        )

        self._root = ft.Column(
            [
                self.header_container,
                ft.Divider(height=1),
                self.chat_container,
                ft.Divider(height=1),
                self.input_container,
            ],
            expand=True,
            spacing=0,
        )

    @property
    def view(self):
        return self._root
    
    def _show_delete_confirmation(self, e):
        message_id = e.control.data
        def confirm_delete(event):
            self._delete_message(message_id)
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this message? This action cannot be undone."),
            actions=[
                ft.TextButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False) or self.page.update())
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _delete_message(self, message_id_to_delete: str):
        indices_to_remove = []
        ids_to_remove = set() 
        for i, msg in enumerate(self.current_chat_messages):
            if msg.get('id') == message_id_to_delete:
                indices_to_remove.append(i)
                ids_to_remove.add(msg.get('id'))
                if msg.get('role') == 'user' and (i + 1) < len(self.current_chat_messages):
                    next_msg = self.current_chat_messages[i+1]
                    if next_msg.get('role') == 'model':
                        indices_to_remove.append(i + 1)
                        ids_to_remove.add(next_msg.get('id'))
                break 
        
        for i in sorted(indices_to_remove, reverse=True):
            del self.current_chat_messages[i]
        
        self.chat_column.controls = [c for c in self.chat_column.controls if c.data not in ids_to_remove]
        
        if self.current_chat_id:
            self.history_manager.update_chat(self.current_chat_id, self.current_chat_messages)
            print(f"Chat {self.current_chat_id} updated after deletion.")
            # self._bot["instance"].load_history(self.current_chat_messages)
        self.page.update()
    
    def _create_delete_icon(self, message_id):
        icon = ft.Icon(
            name=ft.Icons.DELETE_OUTLINE,
            size=16,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )

        def on_hover(e):
            e.control.content.color = ft.Colors.RED if e.data == "true" else ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
            e.control.update()
        
        return ft.Container(
            content=icon,
            data=message_id,
            on_click=self._show_delete_confirmation,
            on_hover=on_hover,
            width=30,
            height=30,
            border_radius=30,
            tooltip="Delete Message",
            alignment=ft.alignment.center
        )

    def _create_edit_icon(self, message_id):
        icon = ft.Icon(
            name=ft.Icons.EDIT_OUTLINED,
            size=16,
            color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
        )

        def on_hover(e):
            e.control.content.color = ft.Colors.BLUE_ACCENT if e.data == "true" else ft.Colors.with_opacity(0.5, ft.Colors.BLACK)
            e.control.update()
        
        return ft.Container(
            content=icon,
            data=message_id,
            on_click=self._start_editing_message,
            on_hover=on_hover,
            width=30,
            height=30,
            border_radius=30,
            tooltip="Edit Message",
            alignment=ft.alignment.center
        )
    
    def _start_editing_message(self, e):
        message_id = e.control.data
        self.editing_message_id = message_id
        
        message_text = ""
        for msg in self.current_chat_messages:
            if msg.get('id') == message_id:
                message_text = msg.get('content')
                break
        
        self.user_input.value = message_text
        self.user_input.label = "Editing message..."
        self.send_btn.icon = ft.Icons.CHECK
        self.send_btn.tooltip = "Confirm Edit"
        self.user_input.focus()
        self.cancel_btn.visible = True
        self.page.update()

    def _exit_editing_mode(self):
        self.editing_message_id = None
        self.user_input.value = ""
        self.user_input.label = "Enter your message"
        self.send_btn.icon = ft.Icons.SEND_ROUNDED
        self.send_btn.tooltip = "Send Message"
        self.cancel_btn.visible = False
        self.page.update()

    def _cancel_edit(self, e):
        self._exit_editing_mode()

    def _show_info_dialog(self, title: str, content):
        content_control = content if isinstance(content, ft.Control) else ft.Text(content)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=content_control,
            actions=[ft.TextButton("OK", on_click=lambda e: setattr(dlg, 'open', False) or self.page.update())],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def _save_chat_click(self, e):
        if not self.current_chat_messages:
            self._show_info_dialog("Cannot save an empty chat!")
            return
        
        if self.current_chat_id:
            self._show_info_dialog("Already Saved", "This chat is already saved and will auto-update.")
            return

        loading_dialog = ft.AlertDialog(modal=True, title=ft.Text("Saving Chat..."), content=ft.Row([ft.ProgressRing(), ft.Text("Generating title...")]))
        
        def do_summarize_and_save_chat():
            try:
                if self._bot["instance"] is None: 
                    self._bot["instance"] = ChatBot(system_prompt=self.current_persona.get("prompt", "..."))

                title = self._bot["instance"].summarize_title(self.current_chat_messages)
                new_id = self.history_manager.save_chat(self.current_persona['id'], self.current_chat_messages, title)
                self.current_chat_id = new_id
                self._show_info_dialog("Success", f"Chat saved with title: '{title}'")
            except Exception as ex:
                self._show_info_dialog("Error", f"Could not save chat: {ex}")
            finally:
                loading_dialog.open = False
                self.page.update()

        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        self.page.update()
        threading.Thread(target=do_summarize_and_save_chat).start()

    def _save_memory_click(self, e):
        if not self.current_chat_messages: 
            return
        
        loading_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Creating Memory..."),
            content=ft.Row([ft.ProgressRing(), ft.Text("The AI is summarizing...")], spacing=20),
        )

        def do_summarize_and_save():
            """This function will run in a separate thread."""
            try:
                if self._bot["instance"] is None:
                    self._bot["instance"] = ChatBot(system_prompt=self.current_persona.get("prompt", "..."))
                
                summary = self._bot["instance"].summarize(self.current_chat_messages)
                self.history_manager.save_memory(self.current_persona['id'], self.current_chat_id, summary)
                
                summary_control = ft.Container(
                    content=ft.Markdown(f"*{summary}*", selectable=True, extension_set="git-hub-flavored"),
                )
                self._show_info_dialog("Memory Saved Successfully", summary_control)

            except Exception as ex:
                self._show_info_dialog("Error", f"Could not create memory: {ex}")
            finally:
                loading_dialog.open = False
                self.page.update()

        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        self.page.update()
        
        thread = threading.Thread(target=do_summarize_and_save)
        thread.start()

    def _new_chat_click(self, e):
        print("New Chat clicked")
        self.start_new_chat(self.current_persona)
        self.page.update()
    
    def start_new_chat(self, persona: dict):
        self.current_persona = persona
        # self._bot["instance"] = None
        self.current_chat_id = None
        self.editing_message_id = None
        self.persona_avatar.content = ft.Image(src=self.current_persona.get("image_path"), fit=ft.ImageFit.COVER, error_content=ft.Icon(ft.Icons.PERSON))
        self.persona_name.value = self.current_persona.get("name", "Unknown")
        self.chat_column.controls.clear()
        self.current_chat_messages.clear()

    def load_chat_history(self, chat: dict):
        self.start_new_chat(self.current_persona)
        self.current_chat_id = chat.get('chat_id')
        messages = chat.get('messages', [])
        for msg in messages: 
            msg.setdefault('id', str(uuid.uuid4()))
        
        self.current_chat_messages = messages

        if self._bot["instance"] is None:
            prompt = self.current_persona.get("prompt", "You are a helpful assistant.")
            self._bot["instance"] = ChatBot(system_prompt=prompt)
        # self._bot["instance"].load_history(messages)
        
        for message in self.current_chat_messages:
            if message.get("role") == "user":
                self._add_user_bubble(message.get("content"), message_id=message.get("id"), record_message=False)
            elif message.get("role") == "model":
                self._add_bot_bubble(message.get("content"), elapsed=0, message_id=message.get("id"), record_message=False)
        
        # self._bot["instance"] = None
        self.page.update()
        
    def _on_resize(self, e=None):
        if not self._root.page:
            return

        page_height = self.page.height
        page_width = self.page.width
        
        self.chat_container.height = page_height - (self.header_container.height + self.input_container.height + 40)

        max_width = page_width * self.BUBBLE_RATIO
        
        for row in self.chat_column.controls:
            if not isinstance(row, ft.Row) or not row.data: 
                continue

            wrapper = None
            if isinstance(row, ft.Row) and len(row.controls) > 0:
                if row.alignment == ft.MainAxisAlignment.START: # Bot message
                    if len(row.controls) > 1: 
                        wrapper = row.controls[1]
                elif row.alignment == ft.MainAxisAlignment.END: # User message
                    wrapper = row.controls[0]

            if isinstance(wrapper, ft.Container) and wrapper is not self.active_bot_wrapper:
                wrapper.width = max_width

        self.page.update()
        
    def _send_message(self, e):
        if self.editing_message_id:
            self._submit_edit()
        else:
            self._send_new_message()

    def _send_new_message(self):
        question = self.user_input.value.strip()
        if not question or not self.current_persona or self.active_loading_row:
            return


        self._add_user_bubble(question)
        self.user_input.value = ""
        self.user_input.focus()
        self.page.update()

        self._get_bot_response(question)

    def _submit_edit(self):
        edited_text = self.user_input.value.strip()
        if not edited_text:
            return

        user_msg_index = -1
        for i, msg in enumerate(self.current_chat_messages):
            if msg.get('id') == self.editing_message_id:
                user_msg_index = i
                break
        
        if user_msg_index == -1:
            self._exit_editing_mode()
            return

        self.current_chat_messages[user_msg_index]['content'] = edited_text
        self.current_chat_messages = self.current_chat_messages[:user_msg_index + 1]

        row_to_update = None
        for control in self.chat_column.controls:
            if control.data == self.editing_message_id:
                row_to_update = control
                break
        
        if row_to_update:
            new_bubble = ft.Container(
                content=ft.Markdown(
                    edited_text,
                    selectable=True,
                    extension_set="git-hub-flavored",
                    code_theme="atom-one-dark"
                ),
                padding=10,
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                border_radius=10,
                border=ft.border.all(0.3, ft.Colors.OUTLINE),
            )

            edit_icon = self._create_edit_icon(self.editing_message_id)
            delete_icon = self._create_delete_icon(self.editing_message_id)

            new_bubble_with_icon = ft.Stack(
                [
                    ft.Container(
                        content=new_bubble,
                        margin=ft.margin.only(bottom=27),
                    ),
                    ft.Container(
                        content=ft.Row([edit_icon, delete_icon], spacing=0, alignment=ft.MainAxisAlignment.END),
                        right=0,
                        bottom=0,
                    ),
                ],
                clip_behavior=ft.ClipBehavior.NONE,
            )

            new_wrapper = ft.Container(
                content=new_bubble_with_icon,
                width=self.page.width * self.BUBBLE_RATIO,
                alignment=ft.alignment.center_right,
                margin=ft.margin.only(right=20),
            )

            row_to_update.controls[0] = new_wrapper
            
            self.chat_column.controls = self.chat_column.controls[:self.chat_column.controls.index(row_to_update) + 1]
        
        self._exit_editing_mode()
        self.page.update()

        self._get_bot_response(edited_text)


    def _get_bot_response(self, question: str):
        if self._bot["instance"] is None:
            prompt = self.current_persona.get("prompt", "You are a helpful assistant.")
            self._bot["instance"] = ChatBot(system_prompt=prompt)

        self.user_input.disabled = True
        self.send_btn.disabled = True
        self.cancel_btn.visible = False
        self._add_bot_loading_bubble()
        self.page.update()
        self._scroll_to_bottom()

        def get_bot_response_thread():

            start_time = time()
            history = self.current_chat_messages[:-1]
            answer = self._bot["instance"].ask(question, history)
            elapsed = time() - start_time

            new_message_id = str(uuid.uuid4())
            self.current_chat_messages.append({"id": new_message_id, "role": "model", "content": answer})
            
            if self.active_bot_bubble and self.active_bot_wrapper and self.active_loading_row:
                final_content_md = f"{answer}\n\n*Response time: {elapsed:.2f} s*"

                bubble = ft.Container(
                    content=ft.Markdown(
                        final_content_md, selectable=True, extension_set="git-hub-flavored", code_theme="atom-one-dark"
                    ),
                    padding=10, 
                    bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_200),
                    border_radius=10, 
                    border=ft.border.all(0.3, ft.Colors.OUTLINE),
                )
                
                icons_row = ft.Row(
                    [
                        self._create_delete_icon(new_message_id),

                    ], 
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                )

                message_stack = ft.Stack(
                    [bubble, ft.Container(
                        content=icons_row,
                        bottom=0,
                        right=0,
                    ),], 
                    clip_behavior=ft.ClipBehavior.NONE,
                )

                wrapper = ft.Container(
                    content=message_stack,
                    width=self.page.width * self.BUBBLE_RATIO,
                    alignment=ft.alignment.center_left,
                )

                self.active_loading_row.controls[1] = wrapper
                self.active_loading_row.data = new_message_id
                
                self.active_bot_bubble = None 
                self.active_bot_wrapper = None
                self.active_loading_row = None

            if self.current_chat_id:
                try:
                    self.history_manager.update_chat(self.current_chat_id, self.current_chat_messages)
                    print(f"Chat {self.current_chat_id} auto-saved.")
                except Exception as ex:
                    print(f"Auto-save failed for chat {self.current_chat_id}: {ex}")

            self.user_input.disabled = False
            self.send_btn.disabled = False

            async def set_focus_async():
                await asyncio.sleep(0.1)
                self.user_input.focus()
                self.page.update()

            asyncio.run_coroutine_threadsafe(set_focus_async(), self.page.loop)

            self.page.update()
            self._scroll_to_bottom()

        threading.Thread(target=get_bot_response_thread).start()

    def _scroll_to_bottom(self):
        self.chat_column.scroll_to(offset=-1, duration=300)

    def _add_user_bubble(self, text: str, message_id: str = None, record_message: bool = True):
        if record_message:
            message_id = str(uuid.uuid4())
            self.current_chat_messages.append({"id": message_id, "role": "user", "content": text})
        elif not message_id:
            message_id = str(uuid.uuid4())

        bubble = ft.Container(
            content=ft.Markdown(text, selectable=True, extension_set="git-hub-flavored", code_theme="atom-one-dark"),
            padding=10,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=10,
            border=ft.border.all(0.3, ft.Colors.OUTLINE),
        )

        edit_icon = self._create_edit_icon(message_id)
        delete_icon = self._create_delete_icon(message_id)

        bubble_with_icon = ft.Stack(
            [
                ft.Container(
                    content=bubble,
                    margin=ft.margin.only(bottom=27),
                ),
                ft.Container(
                    content=ft.Row([edit_icon, delete_icon], spacing=0, alignment=ft.MainAxisAlignment.END),
                    right=0,
                    bottom=0,
                    
                ),
            ],
            clip_behavior=ft.ClipBehavior.NONE,
        )

        wrapper = ft.Container(
            content=bubble_with_icon,
            width=self.page.width * self.BUBBLE_RATIO,
            alignment=ft.alignment.center_right,
            margin=ft.margin.only(right=20),
        )

        self.chat_column.controls.append(
            ft.Row(
                [wrapper], 
                alignment=ft.MainAxisAlignment.END, 
                data=message_id
            )
        )

    def _add_bot_loading_bubble(self):
        loading_bubble = ft.Container(
            content=ft.ProgressRing(width=20, height=20, stroke_width=2.5),
            padding=12, bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_200),
            border_radius=10, border=ft.border.all(0.3, ft.Colors.OUTLINE),
        )
        self.active_bot_bubble = loading_bubble 

        wrapper = ft.Container(
            content=self.active_bot_bubble, 
            width=self.LOADING_BUBBLE_WIDTH,
            alignment=ft.alignment.center_left,
        )
        self.active_bot_wrapper = wrapper

        row = ft.Row(
            [
                ft.Container(
                    content=ft.Image(
                        src=self.current_persona.get("image_path"), 
                        fit=ft.ImageFit.COVER, 
                        error_content=ft.Icon(ft.Icons.PERSON)
                    ),
                    width=40, height=40, border_radius=20, 
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                self.active_bot_wrapper
            ], 
            alignment=ft.MainAxisAlignment.START, 
            vertical_alignment=ft.CrossAxisAlignment.START, 
            spacing=10,
            data=None # No ID yet
        )

        self.active_loading_row = row
        self.chat_column.controls.append(self.active_loading_row)

    def _add_bot_bubble(self, answer: str, elapsed: float, message_id: str = None, record_message: bool = True):
        if record_message:
            if not message_id:
                message_id = str(uuid.uuid4())
            self.current_chat_messages.append({"id": message_id, "role": "model", "content": answer})
        elif not message_id:
            message_id = str(uuid.uuid4())

        content = f"{answer}"
        if elapsed > 0:
            content = f"{answer}\n\n*Response time: {elapsed:.2f} s*"

        bubble = ft.Container(
            content=ft.Markdown(
                content, 
                selectable=True, 
                extension_set="git-hub-flavored", 
                code_theme="atom-one-dark"
            ),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_200),
            border_radius=10,
            border=ft.border.all(0.3, ft.Colors.OUTLINE),
        )

        wrapper = ft.Container(
            content=bubble,
            width=self.page.width * self.BUBBLE_RATIO,
            alignment=ft.alignment.center_left,
        )

        self.chat_column.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Image(
                            src=self.current_persona.get("image_path"), 
                            fit=ft.ImageFit.COVER, 
                            error_content=ft.Icon(ft.Icons.PERSON)
                        ),
                        width=40, 
                        height=40, 
                        border_radius=20, 
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    wrapper
                ], 
                alignment=ft.MainAxisAlignment.START, 
                vertical_alignment=ft.CrossAxisAlignment.START, 
                spacing=10,
                data=message_id
            )
        )