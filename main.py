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

# 2. Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False
# ตั้งค่าเริ่มต้น ถ้ายังไม่มีให้เลือกตัวแรก
if "current_persona" not in st.session_state:
    st.session_state.current_persona = list(config.PERSONAS.keys())[0]

# 3. Sidebar
with st.sidebar:
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=50)
        except: st.write("🤖")
    with col_title:
        st.markdown("## XianBot")

    st.markdown("---")
    
    # 🔥 1. Persona Selector (เลือกนิสัย)
    st.markdown("### 🎭 เลือกนิสัยบอท")
    
    # ดัก Error: ถ้าค่าที่จำไว้มันไม่อยู่ในรายการ (เช่น แก้โค้ดแล้วชื่อเปลี่ยน) ให้รีเซ็ตใหม่
    if st.session_state.current_persona not in config.PERSONAS:
        st.session_state.current_persona = list(config.PERSONAS.keys())[0]

    selected_persona = st.selectbox(
        "เลือกโหมด:",
        list(config.PERSONAS.keys()),
        index=list(config.PERSONAS.keys()).index(st.session_state.current_persona),
        label_visibility="collapsed"
    )
    if selected_persona != st.session_state.current_persona:
        st.session_state.current_persona = selected_persona
        st.toast(f"เปลี่ยนโหมดเป็น: {selected_persona}")

    st.markdown("---")
    
    # Mode Toggle
    if st.session_state.voice_mode:
        if st.button("💬 กลับไปแชท", type="primary", use_container_width=True):
            st.session_state.voice_mode = False
            st.rerun()
    else:
        if st.button("🎙️ โหมดเสียง", type="secondary", use_container_width=True):
            st.session_state.voice_mode = True
            st.rerun()

    st.markdown("---")
    
    # History & Actions
    if not st.session_state.voice_mode:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
            
        # 🔥 2. Download Chat
        chat_log = ""
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Bot"
            content = msg.get("display", msg["content"])
            if isinstance(content, list): content = "[Attached File/Image]"
            chat_log += f"{role}: {content}\n{'-'*20}\n"
            
        st.download_button(
            label="💾 บันทึกแชท (Save)",
            data=chat_log,
            file_name=f"chat_history_{st.session_state.session_id[:8]}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.markdown("---")
        
        st.caption("Recent Chats")
        saved_chats = history.get_chat_history_list()
        for chat in saved_chats:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                if st.button(chat["title"], key=chat["id"], use_container_width=True):
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
# 🔥 MAIN LOGIC
# ==========================================

# --- A. VOICE MODE ---
if st.session_state.voice_mode:
    st.markdown("""<div class="voice-container"><div class="voice-orb"></div><div class="voice-status">แตะไมค์แล้วพูดได้เลย...</div></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        audio_input = st.audio_input("Speak", label_visibility="collapsed")
    
    if audio_input:
        transcript = utils.transcribe_audio(audio_input.getvalue(), api_key)
        if transcript:
            client = Groq(api_key=api_key)
            system_prompt = config.PERSONAS[st.session_state.current_persona] + "\n(ตอบสั้นๆ)"
            msgs = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages[-4:]:
                c = m.get("display", m["content"])
                if isinstance(c, str): msgs.append({"role": m["role"], "content": c})
            msgs.append({"role": "user", "content": transcript})

            try:
                resp = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile").choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": transcript, "display": transcript})
                st.session_state.messages.append({"role": "assistant", "content": resp})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
                utils.text_to_speech(resp)
            except Exception as e: st.error(f"Error: {e}")

# --- B. CHAT MODE ---
else:
    if not st.session_state.messages:
        c1, c2, c3 = st.columns([1.5, 1, 1.5])
        with c2:
            try: st.image("logo.png")
            except: st.markdown("# 🤖")
        st.markdown(f"<h3 style='text-align: center; color: #666;'>XianBot Pro<br><span style='font-size: 0.6em; color: #888;'>Mode: {st.session_state.current_persona}</span></h3>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="logo.png" if msg["role"] == "assistant" else None):
            d = msg.get("display", msg["content"])
            if isinstance(d, list): 
                for p in d:
                    if p["type"]=="text": st.markdown(p["text"])
                    if p["type"]=="image_url": st.image(p["image_url"]["url"], width=400)
            else: st.markdown(d)

    with st.container():
        uploaded_file = st.file_uploader("แนบไฟล์", label_visibility="collapsed")
        f_ctx, f_img = "", None
        if uploaded_file:
            st.toast(f"✅ แนบไฟล์: {uploaded_file.name}")
            if "image" in uploaded_file.type: f_img = utils.encode_image(uploaded_file)
            else: f_ctx = utils.extract_file(uploaded_file)

    prompt = st.chat_input("พิมพ์ข้อความ... หรือแปะลิงก์ YouTube")

    if prompt:
        real_load = prompt
        disp_load = prompt

        if "youtube.com" in prompt or "youtu.be" in prompt:
            st.toast("กำลังแกะคลิป...", icon="📺")
            with st.spinner("Analyzing..."):
                transcript = utils.get_youtube_content(prompt, api_key)
                if transcript: real_load = f"สรุปคลิปนี้ (ไทย):\n{transcript}"
                else: st.error("แกะคลิปไม่ได้"); st.stop()

        elif f_img: real_load = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{f_img}"}}]
        elif f_ctx: real_load = f"{prompt}\n\n---\n{f_ctx}"

        st.session_state.messages.append({"role": "user", "content": real_load, "display": disp_load})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                # 🔥 เรียกใช้ PERSONAS จาก config
                system_prompt = config.PERSONAS[st.session_state.current_persona]
                msgs = [{"role": "system", "content": system_prompt}]
                
                for m in st.session_state.messages[:-1]:
                    c = m.get("content")
                    if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                    if c: msgs.append({"role": m["role"], "content": str(c)})
                
                last = st.session_state.messages[-1]["content"]
                msgs.append({"role": "user", "content": last})
                
                model = "meta-llama/llama-4-scout-17b-16e-instruct" if isinstance(last, list) else "llama-3.3-70b-versatile"
                
                stream = client.chat.completions.create(messages=msgs, model=model, stream=True)
                box = st.empty()
                full = ""
                for ch in stream:
                    if ch.choices[0].delta.content:
                        full += ch.choices[0].delta.content
                        box.markdown(full + "▌")
                box.markdown(full)
                st.session_state.messages.append({"role": "assistant", "content": full})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
            except Exception as e: st.error(str(e))