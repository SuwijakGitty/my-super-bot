import json
import os
import uuid
from datetime import datetime

HISTORY_DIR = "chats"

# สร้างโฟลเดอร์ถ้ายังไม่มี
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def save_chat(session_id, messages, title=None):
    if not messages: return
    
    # ถ้ายังไม่มีชื่อเรื่อง ให้เอาข้อความแรกมาตั้งชื่อ
    if not title:
        for m in messages:
            if m["role"] == "user":
                title = m["content"][:30] + "..." if isinstance(m["content"], str) else "รูปภาพ..."
                break
        if not title: title = "New Chat"

    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    data = {
        "id": session_id,
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_chat(session_id):
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["messages"]
    return []

def get_chat_history_list():
    chats = []
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(HISTORY_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chats.append({
                        "id": data["id"],
                        "title": data.get("title", "No Title"),
                        "timestamp": data.get("timestamp", "")
                    })
            except: pass
    # เรียงจากใหม่ไปเก่า
    chats.sort(key=lambda x: x["timestamp"], reverse=True)
    return chats

def delete_chat(session_id):
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)