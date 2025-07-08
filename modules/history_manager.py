import json
import os
from datetime import datetime
import uuid

class HistoryManager:
    CHATS_FILE = "assets/saved_chats.json"
    MEMORIES_FILE = "assets/saved_memories.json"

    def __init__(self):
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
            chats = json.load(f)

        for chat in chats:
            for msg in chat.get('messages', []):
                if msg['role'] == 'bot':
                    msg['role'] = 'model'
        return chats

    def save_chat(self, persona_id: str, messages: list, title: str) -> str:
        if not messages:
            return # Don't save empty chats
        
        messages = [
            {"id": msg["id"], "role": "model" if msg["role"] == "bot" else msg["role"], "content": msg["content"]}
            for msg in messages
        ]

        chats = self.load_chats()
        
        new_chat = {
            "chat_id": uuid.uuid4().hex,
            "persona_id": persona_id,
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "title": title
        }
        
        chats.append(new_chat)
        self._write_json(self.CHATS_FILE, chats)
        print(f"Chat {new_chat['chat_id']} saved.")
        return new_chat['chat_id']
    
    def update_chat(self, chat_id: str, messages: list):
        if not chat_id: 
            return
        
        messages = [
            {"id": msg["id"], "role": "model" if msg["role"] == "bot" else msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        chats = self.load_chats()
        chat_found = False
        for i, chat in enumerate(chats):
            if chat.get('chat_id') == chat_id:
                chats[i]['messages'] = messages
                chat_found = True
                break
            
        if chat_found:
            self._write_json(self.CHATS_FILE, chats)
    
    def delete_chat(self, chat_id: str):
        chats = self.load_chats()
        updated_chats = [chat for chat in chats if chat.get('chat_id') != chat_id]
        self._write_json(self.CHATS_FILE, updated_chats)
        print(f"Chat {chat_id} deleted.")

    def save_memory(self, persona_id: str, chat_id: str | None, summary: str):
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
        
    def delete_memory(self, memory_id: str):
        memories = self.load_memories()
        updated_memories = [m for m in memories if m.get('memory_id') != memory_id]
        self._write_json(self.MEMORIES_FILE, updated_memories)
        print(f"Memory {memory_id} deleted.")