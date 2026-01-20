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
    if not st.session_state.voice_mode:
        with st.expander("💡 วิธีใช้ (New!)"):
            st.markdown("""
            - **สรุป YouTube:** แปะลิงก์คลิป (ถ้าไม่มีซับ ต้องมี ffmpeg.exe)
            - **ค้นหา:** พิมพ์ `/search` ตามด้วยคำถาม
            """)
    st.markdown("---")
    
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
        # (ส่วน History โค้ดเดิม)
        saved_chats = history.get_chat_history_list()
        for chat in saved_chats:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                 if st.button((chat["title"][:18]+'..') if len(chat["title"])>18 else chat["title"], key=chat["id"], use_container_width=True):
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
# 🔥 MAIN APP LOGIC
# ==========================================
if st.session_state.voice_mode:
    st.markdown("""<div class="voice-container"><div class="voice-orb"></div><div class="voice-status">แตะไมค์แล้วพูดได้เลย...</div></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        audio_input = st.audio_input("แตะเพื่อพูด", label_visibility="collapsed")
    
    if audio_input:
        transcript = utils.transcribe_audio(audio_input.getvalue(), api_key)
        if transcript:
            # (Logic Voice Mode เหมือนเดิม)
            client = Groq(api_key=api_key)
            msgs = [{"role": "system", "content": config.SYSTEM_PROMPT}]
            msgs.append({"role": "user", "content": transcript})
            try:
                chat_completion = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1000)
                response_text = chat_completion.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": transcript})
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
                audio_fp = utils.text_to_speech(response_text)
                if audio_fp: st.audio(audio_fp, format='audio/wav', autoplay=True)
            except Exception as e: st.error(f"Error: {e}")

else:
    # 1. Header
    if not st.session_state.messages:
        try: st.image("logo.png", width=120) 
        except: st.markdown("# 🤖")
        st.markdown("<h1 style='text-align: center;'>XianBot Pro</h1>", unsafe_allow_html=True)

    # 2. Render Chat
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = None if role == "user" else "logo.png"
        with st.chat_message(role, avatar=avatar):
            content = msg["content"]
            # ถ้ามี content ที่ซ่อนอยู่ (สำหรับการแสดงผล)
            display_text = msg.get("display", content)
            
            if isinstance(display_text, list):
                for p in display_text:
                    if p["type"]=="text": st.markdown(p["text"])
                    if p["type"]=="image_url": st.image(p["image_url"]["url"], width=500)
            else: 
                st.markdown(display_text)

    # 3. File Upload
    with st.container():
        uploaded_file = st.file_uploader("📎 แนบไฟล์", label_visibility="collapsed")
        file_context = ""
        file_image_data = None
        if uploaded_file:
            st.success(f"แนบไฟล์: {uploaded_file.name}")
            if "image" in uploaded_file.type:
                file_image_data = utils.encode_image(uploaded_file)
            else:
                file_context = utils.extract_file(uploaded_file)

    # 4. Input & Logic
    if prompt := st.chat_input("พิมพ์ข้อความ... หรือ /search", key="main_input"):
        
        real_payload = prompt
        display_payload = prompt # สิ่งที่จะโชว์ในแชท

        # --- ตรวจจับฟีเจอร์ ---
        
        # 📺 1. YouTube
        if "youtube.com" in prompt or "youtu.be" in prompt:
            st.toast("📺 กำลังแกะเนื้อหาคลิป YouTube...", icon="⏳")
            with st.spinner("กำลังดูดเสียงและแกะเนื้อหา (ใช้เวลาสักครู่)..."):
                transcript = utils.get_youtube_content(prompt, api_key)
                if transcript:
                    real_payload = f"สรุปคลิปนี้ให้หน่อย (ภาษาไทย):\n\n{transcript}"
                    st.toast("✅ แกะเนื้อหาเสร็จแล้ว!", icon="🎉")
                else:
                    st.error("แกะเนื้อหาไม่ได้ครับ (เช็คว่ามี ffmpeg.exe หรือยัง?)")
                    st.stop()
        
        # 🌐 2. Search
        elif prompt.startswith("/search"):
            st.toast("🌐 กำลังค้นหาข้อมูล...", icon="🔍")
            query = prompt.replace("/search", "").strip()
            web_result = utils.search_web(query)
            real_payload = f"User asked: {query}\n\nSearch Results:\n{web_result}\n\nAnswer the user based on results:"
            st.toast("✅ ค้นหาเสร็จสิ้น!", icon="🎉")

        # 🖼️ 3. Image/File
        elif file_image_data:
            real_payload = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{file_image_data}"}}]
        elif file_context:
            real_payload = f"{prompt}\n\n[File Content]:\n{file_context}"

        # บันทึกและ Rerun
        st.session_state.messages.append({"role": "user", "content": real_payload, "display": display_payload})
        st.rerun()

    # 5. AI Reply
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                msgs = [{"role": "system", "content": config.SYSTEM_PROMPT}]
                
                # History Loop
                for m in st.session_state.messages[:-1]:
                    c = m["content"]
                    if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                    msgs.append({"role": m["role"], "content": c})
                
                # Last Message
                last_msg = st.session_state.messages[-1]["content"]
                msgs.append({"role": "user", "content": last_msg})
                
                model = "llama-3.2-90b-vision-preview" if isinstance(last_msg, list) else "llama-3.3-70b-versatile"
                
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
            except Exception as e: st.error(f"Error: {e}")