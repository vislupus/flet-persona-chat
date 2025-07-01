import json
import os
from datetime import datetime
import uuid

class HistoryManager:
    CHATS_FILE = "saved_chats.json"
    MEMORIES_FILE = "saved_memories.json"

    def __init__(self):
        # Ensure files exist
        if not os.path.isfile(self.CHATS_FILE):
            self._write_json(self.CHATS_FILE, [])
        if not os.path.isfile(self.MEMORIES_FILE):
            self._write_json(self.MEMORIES_FILE, [])

    def _write_json(self, file_path, data):
        """Helper to write data to a JSON file."""
        with open(file_path, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_chats(self) -> list:
        """Loads all saved chat sessions."""
        with open(self.CHATS_FILE, "r", encoding="utf8") as f:
            return json.load(f)

    def save_chat(self, persona_id: str, messages: list):
        """Saves a new chat session."""
        if not messages:
            return # Don't save empty chats

        chats = self.load_chats()
        
        new_chat = {
            "chat_id": uuid.uuid4().hex,
            "persona_id": persona_id,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "title": f"Chat from {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
        
        chats.append(new_chat)
        self._write_json(self.CHATS_FILE, chats)
        print(f"Chat {new_chat['chat_id']} saved.")

    def save_memory(self, persona_id: str, chat_id: str, summary: str):
        memories = self.load_memories()
        
        new_memory = {
            "memory_id": uuid.uuid4().hex,
            "persona_id": persona_id,
            "chat_id": chat_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        memories.append(new_memory)
        self._write_json(self.MEMORIES_FILE, memories)
        print(f"Memory {new_memory['memory_id']} saved.")

    def load_memories(self) -> list:
        with open(self.MEMORIES_FILE, "r", encoding="utf8") as f:
            return json.load(f)