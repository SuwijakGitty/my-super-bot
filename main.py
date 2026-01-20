import streamlit as st
from groq import Groq
import uuid

# Import Modules
import config
import styles
import utils
import history

# 1. Setup
config.setup_page()
styles.load_css()
api_key = config.get_api_key()

# 2. Session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

# 3. Sidebar
with st.sidebar:
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=60)
        except: st.write("🤖")
    with col_title:
        st.markdown("## XianBot")

    st.markdown("---")

    # ปุ่มสลับ Voice Mode
    if st.session_state.voice_mode:
        if st.button("💬 กลับไปหน้าแชท", type="primary", use_container_width=True):
            st.session_state.voice_mode = False
            st.rerun()
    else:
        if st.button("🎙️ เข้าโหมดเสียง (Voice Mode)", type="secondary", use_container_width=True):
            st.session_state.voice_mode = True
            st.rerun()

    st.markdown("---")
    
    if not st.session_state.voice_mode:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
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

# ==========================================
# 🔥 MODE 1: VOICE MODE
# ==========================================
if st.session_state.voice_mode:
    # (ส่วน Voice Mode เหมือนเดิม)
    st.markdown("""<div class="voice-container"><div class="voice-orb"></div><div class="voice-status">แตะไมค์แล้วพูดได้เลย...</div></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        audio_input = st.audio_input("แตะเพื่อพูด", label_visibility="collapsed")
    
    if audio_input:
        transcript = utils.transcribe_audio(audio_input.getvalue(), api_key)
        if transcript:
            client = Groq(api_key=api_key)
            msgs = [{"role": "system", "content": config.SYSTEM_PROMPT + "\n(Context: Voice Call, concise.)"}]
            for m in st.session_state.messages[-6:]:
                c = m["content"]
                if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                msgs.append({"role": m["role"], "content": c})
            msgs.append({"role": "user", "content": transcript})

            try:
                chat_completion = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1000)
                response_text = chat_completion.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": transcript})
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
                
                has_thai = any('\u0e00' <= char <= '\u0e7f' for char in response_text)
                speak_lang = 'th' if has_thai else 'en'
                audio_fp = utils.text_to_speech(response_text, lang=speak_lang)
                if audio_fp: st.audio(audio_fp, format='audio/wav', autoplay=True)
                
            except Exception as e: st.error(f"Error: {e}")

# ==========================================
# 🔥 MODE 2: CHAT MODE (ปกติ)
# ==========================================
else:
    # 1. Header
    if not st.session_state.messages:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try: st.image("logo.png", width=120, use_column_width=False, style={"display": "block", "margin-left": "auto", "margin-right": "auto"})
            except: st.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; background: linear-gradient(74deg, #4285f4 0%, #9b72cb 19%, #d96570 30%, #1f1f1f 60%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>XianBot Pro</h1>", unsafe_allow_html=True)
        
        # Shortcuts
        col1, col2 = st.columns(2)
        st.markdown("""<style>div[data-testid="column"] > div > div > div > div > div > button {height: 80px; width: 100%; border-radius: 12px; text-align: left; padding-left: 20px; display: flex; flex-direction: column; align-items: flex-start; justify-content: center;}</style>""", unsafe_allow_html=True)
        with col1:
            if st.button("🚀 วางแผนเที่ยว", key="btn1", use_container_width=True): 
                st.session_state.messages.append({"role": "user", "content": "วางแผนเที่ยวญี่ปุ่น 5 วัน"}); st.rerun()
            if st.button("📝 ฝึกภาษาอังกฤษ", key="btn2", use_container_width=True): 
                st.session_state.messages.append({"role": "user", "content": "Let's practice English conversation."}); st.rerun()
        with col2:
            if st.button("🐍 สอน Python", key="btn3", use_container_width=True): 
                st.session_state.messages.append({"role": "user", "content": "สอนเขียน Python Web Scraping"}); st.rerun()
            if st.button("🍳 คิดเมนูอาหาร", key="btn4", use_container_width=True): 
                st.session_state.messages.append({"role": "user", "content": "มีไก่ ไข่ ข้าว ทำเมนูอะไรดี?"}); st.rerun()

    # 2. Render Chat History
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = None if role == "user" else "logo.png"
        with st.chat_message(role, avatar=avatar):
            if isinstance(msg["content"], list):
                for p in msg["content"]:
                    if p["type"]=="text": st.markdown(p["text"])
                    if p["type"]=="image_url": st.image(p["image_url"]["url"], width=500)
            else: 
                st.markdown(msg["content"])

    # 3. 🔥 File Upload Area (ย้ายมาไว้ตรงนี้ให้เห็นชัดๆ)
    # เราใช้ Container ครอบไว้เหนือช่องแชท เพื่อจำลองความรู้สึก "แนบไฟล์"
    with st.container():
        # สร้างคอลัมน์เพื่อให้ปุ่มแนบไฟล์ดูดีขึ้น
        uploaded_file = st.file_uploader("📎 แนบไฟล์ (รูปภาพ / PDF / Word / Excel / CSV)", label_visibility="collapsed")
        
        # ตัวแปรเก็บเนื้อหาไฟล์
        file_context = ""
        file_image_data = None
        
        if uploaded_file:
            # โชว์สถานะว่าอ่านไฟล์แล้ว
            st.success(f"✅ แนบไฟล์: {uploaded_file.name} เรียบร้อย!")
            
            # ถ้าเป็นรูปภาพ -> เตรียมส่งแบบ Vision
            if "image" in uploaded_file.type:
                file_image_data = utils.encode_image(uploaded_file)
            # ถ้าเป็นเอกสาร -> แกะเนื้อหาออกมาเป็น Text
            else:
                file_context = utils.extract_file(uploaded_file)

    # 4. Input Handling
    if prompt := st.chat_input("พิมพ์ข้อความ / Type here... 😊"):
        
        # เตรียมข้อความที่จะส่งให้ AI (User Message)
        user_content = prompt
        
        # กรณี 1: มีรูปภาพ
        if file_image_data:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{file_image_data}"}}
            ]
        
        # กรณี 2: มีไฟล์เอกสาร (PDF/Word/Excel) -> ยัดเนื้อหาลงไปใน Prompt เลย
        elif file_context:
            # 🔥 เทคนิค: เอาเนื้อหาไฟล์แปะต่อท้ายคำถาม user เลย บอทจะได้เห็นแน่นอน
            full_prompt_with_context = f"{prompt}\n\n---\n[Attached File Content]:\n{file_context}"
            # บันทึกแบบ User เห็นแค่คำถาม (แต่ AI เห็นไฟล์) - หรือจะให้เห็นไฟล์ด้วยก็ได้
            # ในที่นี้ให้ AI เห็นเต็มๆ แต่เก็บใน History อาจจะเก็บยาวหน่อย
            user_content = full_prompt_with_context

        # บันทึกและแสดงผล
        st.session_state.messages.append({"role": "user", "content": user_content})
        st.rerun()

    # 5. AI Chat Logic
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        last_msg = st.session_state.messages[-1]
        
        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                # System Prompt พื้นฐาน
                msgs = [{"role": "system", "content": config.SYSTEM_PROMPT}]
                
                # ดึงประวัติการคุย
                for m in st.session_state.messages[-10:-1]:
                    c = m["content"]
                    if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                    msgs.append({"role": m["role"], "content": c})
                
                # ข้อความล่าสุด (ที่มีเนื้อหาไฟล์ผสมอยู่แล้ว)
                current_content = last_msg["content"]
                if isinstance(current_content, list): 
                    # ถ้าเป็นรูปภาพ ต้องส่งแบบ List
                    msgs.append({"role": "user", "content": current_content})
                    model = "llama-3.2-90b-vision-preview" # 🔥 ใช้โมเดล Vision ถ้ามีรูป
                else:
                    # ถ้าเป็น Text (รวมถึง Text ที่แกะจากไฟล์แล้ว)
                    msgs.append({"role": "user", "content": current_content})
                    model = "llama-3.3-70b-versatile"

                # ยิง API
                stream = client.chat.completions.create(messages=msgs, model=model, temperature=0.7, max_tokens=4000, stream=True)
                
                text_box = st.empty()
                full_response = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        text_box.markdown(full_response + "▌")
                text_box.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    st.markdown('<div class="disclaimer-text">XianBot อาจแสดงข้อมูลที่ไม่ถูกต้อง โปรดตรวจสอบคำตอบอีกครั้ง</div>', unsafe_allow_html=True)