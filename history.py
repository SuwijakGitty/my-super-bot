import json
import os

HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_chat_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_chat_history_list():
    history = load_chat_history()
    return [{"id": h["id"], "title": h["title"]} for h in reversed(history)]

def load_chat(session_id):
    history = load_chat_history()
    for h in history:
        if h["id"] == session_id:
            return h["messages"]
    return []

def save_chat(session_id, messages):
    if not messages: return

    history = load_chat_history()
    
    # 1. สร้างชื่อหัวข้อแบบฉลาด (Smart Title) 🧠
    first_msg = messages[0]
    user_text = ""
    
    # 🔥 แก้ตรงนี้: ให้ดู 'display' (สิ่งที่ user พิมพ์) ก่อน
    # ถ้าไม่มีค่อยไปดู 'content' (สิ่งที่ส่งให้ AI)
    display_text = first_msg.get("display")
    content = first_msg.get("content")

    if isinstance(content, list):
        user_text = "🖼️ วิเคราะห์รูปภาพ"
    elif display_text:
        user_text = str(display_text)
    else:
        user_text = str(content)

    # ตั้งชื่อตามประเภทการใช้งาน
    title = user_text
    
    # เช็คคีย์เวิร์ด
    if "youtube.com" in user_text or "youtu.be" in user_text:
        title = "📺 สรุป YouTube"
    elif "/search" in user_text:
        query = user_text.replace("/search", "").strip()
        title = f"🌐 ค้นหา: {query[:15]}"
    elif "attached file" in str(content).lower() or "[File Content]" in str(content):
        title = "📄 สรุปเอกสาร"
    elif "image_url" in str(content):
         title = "🖼️ วิเคราะห์รูปภาพ"
    else:
        # ถ้าคุยเล่นปกติ เอาสั้นๆ
        title = user_text[:25]

    # 2. บันทึกลงไฟล์
    found = False
    for h in history:
        if h["id"] == session_id:
            h["messages"] = messages
            # อัปเดตชื่อเฉพาะตอนเริ่มคุยครั้งแรกๆ
            if len(h["messages"]) <= 2: 
                h["title"] = title
            found = True
            break
    
    if not found:
        history.append({"id": session_id, "title": title, "messages": messages})
    
    save_chat_history(history)

def delete_chat(session_id):
    history = load_chat_history()
    history = [h for h in history if h["id"] != session_id]
    save_chat_history(history)