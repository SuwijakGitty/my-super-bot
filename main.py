import streamlit as st
from groq import Groq
import uuid

# Import Modules
import config
import styles
import utils
import history

# 1. Setup & Config
config.setup_page()
styles.load_css()
api_key = config.get_api_key()

# 2. Session Management
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar (เปลี่ยนชื่อเป็น XianBot พร้อมโลโก้)
with st.sidebar:
    # จัดโลโก้คู่กับชื่อบอท
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=60)
        except: st.write("🤖") # ถ้าหาโลโก้ไม่เจอใช้ไอคอนนี้แทน
    with col_title:
        st.markdown("## XianBot")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.caption("Recent Chats")
    saved_chats = history.get_chat_history_list()
    for chat in saved_chats:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            display_title = (chat["title"][:18] + '..') if len(chat["title"]) > 18 else chat["title"]
            if st.button(display_title, key=chat["id"], use_container_width=True):
                st.session_state.session_id = chat["id"]
                st.session_state.messages = history.load_chat(chat["id"])
                st.rerun()
        with col2:
            if st.button("✕", key=f"del_{chat['id']}"):
                history.delete_chat(chat["id"])
                if st.session_state.session_id == chat["id"]:
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun()

# 4. Welcome Screen (หน้าต้อนรับแบบ XianBot)
if not st.session_state.messages:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: # พยายามแสดงโลโก้ตรงกลาง
            st.image("logo.png", width=120, use_column_width=False, style={"display": "block", "margin-left": "auto", "margin-right": "auto"})
        except: st.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
        
        st.markdown("""
            <h1 style="text-align: center; background: linear-gradient(74deg, #4285f4 0%, #9b72cb 19%, #d96570 30%, #1f1f1f 60%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                XianBot พร้อมรับคำสั่ง!
            </h1>
        """, unsafe_allow_html=True)
    
    # (Starter Chips โค้ดเดิม... ละไว้ในฐานที่เข้าใจ)
    # ... (ใส่โค้ดปุ่มแนะนำ 4 ปุ่มเดิมตรงนี้) ...
    col1, col2_chips = st.columns(2)
    # CSS เฉพาะปุ่มแนะนำ
    st.markdown("""<style>div[data-testid="column"] > div > div > div > div > div > button {height: 80px; width: 100%; border-radius: 12px; text-align: left; padding-left: 20px; display: flex; flex-direction: column; align-items: flex-start; justify-content: center;}</style>""", unsafe_allow_html=True)
    with col1:
        if st.button("🚀 วางแผนเที่ยวญี่ปุ่น\n(เน้นกิน 5 วัน)", key="btn1", use_container_width=True): st.session_state.messages.append({"role": "user", "content": "ช่วยวางแผนเที่ยวญี่ปุ่น 5 วัน เน้นกินให้หน่อย"}); st.rerun()
        if st.button("📝 ร่างอีเมลสมัครงาน\n(ตำแหน่ง Marketing)", key="btn2", use_container_width=True): st.session_state.messages.append({"role": "user", "content": "ร่างอีเมลสมัครงานภาษาอังกฤษ ตำแหน่ง Marketing ให้หน่อย"}); st.rerun()
    with col2_chips:
        if st.button("🐍 เขียน Python Script\n(ดึงข้อมูลเว็บไซต์)", key="btn3", use_container_width=True): st.session_state.messages.append({"role": "user", "content": "สอนเขียน Python Web Scraping หน่อย"}); st.rerun()
        if st.button("🍳 คิดเมนูอาหารเย็น\n(วัตถุดิบ: ไก่, ไข่)", key="btn4", use_container_width=True): st.session_state.messages.append({"role": "user", "content": "มีไก่ ไข่ ข้าว ทำเมนูอะไรกินดี?"}); st.rerun()


# 5. Render Chat
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = None if role == "user" else "logo.png" # ใช้โลโก้เราเป็น Avatar บอท!
    with st.chat_message(role, avatar=avatar):
        if isinstance(msg["content"], list):
            for p in msg["content"]:
                if p["type"]=="text": st.markdown(p["text"])
                if p["type"]=="image_url": st.image(p["image_url"]["url"], width=300)
        else: st.markdown(msg["content"])

# 6. Input Area (ปุ่มแนบไฟล์ + ปุ่มอัดเสียง!)
with st.container():
    col_audio, col_file = st.columns([0.85, 0.15])
    with col_file:
        with st.popover("📎", help="แนบไฟล์"):
            uploaded_file = st.file_uploader("Upload", label_visibility="collapsed")
            file_txt = utils.extract_file(uploaded_file) if uploaded_file and "image" not in uploaded_file.type else ""
    with col_audio:
        # 🔥 ปุ่มไมโครโฟน (ของใหม่!)
        audio_input = st.audio_input("กดเพื่อพูด...", label_visibility="collapsed")

# 7. Logic (จัดการข้อความและเสียง)
prompt = st.chat_input("พิมพ์ข้อความที่นี่...")
user_content = None

# ถ้ามีการอัดเสียง
if audio_input:
    with st.spinner("👂 XianBot กำลังฟัง..."):
        # แปลงเสียงเป็นข้อความ
        transcript = utils.transcribe_audio(audio_input.getvalue(), api_key)
    if transcript and not transcript.startswith("เกิดข้อผิดพลาด"):
        prompt = transcript # เอาข้อความที่ได้มาเป็น prompt
        st.toast(f"🗣️ คุณพูดว่า: {prompt}", icon="🎙️") # แจ้งเตือนว่าได้ยินว่าอะไร

# ถ้ามี Prompt (จากการพิมพ์ หรือแปลงจากเสียง)
if prompt:
    st.chat_message("user").markdown(prompt)
    user_content = prompt
    system_instruction = config.SYSTEM_PROMPT

    if uploaded_file:
        if "image" in uploaded_file.type:
            img = utils.encode_image(uploaded_file)
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]
        else: system_instruction += f"\n\n[Context]: {file_txt}"
    
    st.session_state.messages.append({"role": "user", "content": user_content})
    st.rerun()

# 8. AI Generation & TTS (บอทตอบ + พูด)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # (Logic เตรียม Prompt เหมือนเดิม... ละไว้)
    system_instruction = config.SYSTEM_PROMPT
    last_msg = st.session_state.messages[-1]
    if uploaded_file and "image" not in uploaded_file.type: system_instruction += f"\n\n[Context]: {file_txt}"

    with st.chat_message("assistant", avatar="logo.png"):
        try:
            client = Groq(api_key=api_key)
            # (Logic เตรียม Messages... ละไว้)
            msgs = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[:-1]:
                c = m["content"]
                if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                msgs.append({"role": m["role"], "content": c})
            msgs.append({"role": "user", "content": last_msg["content"]})

            model = "llama-3.3-70b-versatile"
            if isinstance(last_msg["content"], list): model = "meta-llama/llama-4-scout-17b-16e-instruct"

            # ยิง API แบบ Stream
            stream = client.chat.completions.create(messages=msgs, model=model, temperature=0.7, max_tokens=4000, stream=True)
            
            # Placeholder สำหรับข้อความและเสียง
            text_box = st.empty()
            audio_box = st.empty()
            
            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    text_box.markdown(full_response + "▌")

            text_box.markdown(full_response) # แสดงข้อความเต็ม
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            history.save_chat(st.session_state.session_id, st.session_state.messages)
            
            # 🔥 สร้างเสียงพูด (TTS) ถ้าข้อความไม่ยาวเกินไป
            if len(full_response) < 500: # จำกัดความยาวนิดนึง เดี๋ยวรอนาน
                with st.spinner("👄 XianBot กำลังเตรียมพูด..."):
                    audio_fp = utils.text_to_speech(full_response, lang='th')
                    if audio_fp:
                        # เล่นเสียงอัตโนมัติ!
                        audio_box.audio(audio_fp, format='audio/wav', autoplay=True)

        except Exception as e: st.error(f"Error: {e}")

# Footer
st.markdown('<div class="disclaimer-text">XianBot อาจแสดงข้อมูลที่ไม่ถูกต้อง โปรดตรวจสอบคำตอบอีกครั้ง</div>', unsafe_allow_html=True)