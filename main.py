import streamlit as st
from groq import Groq
import uuid
import pandas as pd
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

# 3. Sidebar
with st.sidebar:
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=50)
        except: st.write("🤖")
    with col_title:
        st.markdown("## XianBot")
    
    st.caption("🚀 Version: Production Build")
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
    
    if not st.session_state.voice_mode:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
        
        # Download Chat
        chat_log = ""
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Bot"
            content = msg.get("display", msg["content"])
            if isinstance(content, list): content = "[File Attached]"
            chat_log += f"{role}: {content}\n{'-'*20}\n"
            
        st.download_button(
            label="💾 Save Chat",
            data=chat_log,
            file_name=f"chat_{st.session_state.session_id[:6]}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==========================================
# 🔥 MAIN LOGIC
# ==========================================

# --- A. VOICE MODE ---
if st.session_state.voice_mode:
    st.markdown("""<div class="voice-container"><div class="voice-orb"></div><div class="voice-status">แตะไมค์แล้วพูด...</div></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        audio_input = st.audio_input("Speak", label_visibility="collapsed")
    
    if audio_input:
        transcript = utils.transcribe_audio(audio_input.getvalue(), api_key)
        if transcript:
            client = Groq(api_key=api_key)
            msgs = [{"role": "system", "content": "ตอบสั้นๆ"}]
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
            except Exception as e: st.error(str(e))

# --- B. CHAT MODE ---
else:
    if not st.session_state.messages:
        c1, c2, c3 = st.columns([1.5, 1, 1.5])
        with c2:
            try: st.image("logo.png")
            except: st.markdown("# 🤖")
        st.markdown(f"<h3 style='text-align: center; color: #666;'>XianBot Pro<br><span style='font-size: 0.6em; color: #28a745;'>Web Edition</span></h3>", unsafe_allow_html=True)

    # 1. Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="logo.png" if msg["role"] == "assistant" else None):
            d = msg.get("display", msg["content"])
            if isinstance(d, str) and "[CHART_DATA]" in d:
                if "last_df" in st.session_state:
                    st.line_chart(st.session_state.last_df)
                d = d.replace("[CHART_DATA]", "")
            
            if isinstance(d, list): 
                for p in d:
                    if p["type"]=="text": st.markdown(p["text"])
            else: st.markdown(d)

    # 2. Upload File (Excel/CSV/PDF)
    with st.container():
        uploaded_file = st.file_uploader("แนบไฟล์ (Excel / CSV / PDF)", type=["pdf", "csv", "xlsx"], label_visibility="collapsed")
        f_ctx = ""
        if uploaded_file:
            if "csv" in uploaded_file.type or "excel" in uploaded_file.type:
                try:
                    if "csv" in uploaded_file.name: df = pd.read_csv(uploaded_file)
                    else: df = pd.read_excel(uploaded_file)
                    st.session_state.last_df = df.select_dtypes(include=['float', 'int'])
                    f_ctx = f"Data: {df.head(20).to_markdown()}"
                    with st.expander(f"🔎 ดูข้อมูล ({len(df)} แถว)"): st.dataframe(df)
                except: st.error("อ่านไฟล์ไม่ได้")
            else:
                f_ctx = utils.extract_file(uploaded_file)

    # 3. Chat Input
    prompt = st.chat_input("พิมพ์ข้อความ...")

    if prompt:
        real_load = prompt
        disp_load = prompt
        
        # Logic YouTube
        if "youtube.com" in prompt or "youtu.be" in prompt:
            with st.spinner("Analyzing..."):
                transcript = utils.get_youtube_content(prompt, api_key)
                if transcript: real_load = f"สรุปคลิปนี้ (ไทย):\n\n{transcript}"
                else: st.error("แกะคลิปไม่ได้"); st.stop()
        
        # Logic File Context
        elif f_ctx: 
            real_load = f"{prompt}\n\n---\n[Context]:\n{f_ctx}"
            if "last_df" in st.session_state: real_load += "\n(Reply '[CHART_DATA]' if visualization needed.)"

        st.session_state.messages.append({"role": "user", "content": real_load, "display": disp_load})
        
        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                msgs = [{"role": "system", "content": "คุณคือ XianBot"}]
                for m in st.session_state.messages[:-1]:
                    if isinstance(m["content"], str): msgs.append({"role": m["role"], "content": m["content"]})
                
                msgs.append({"role": "user", "content": real_load})
                
                stream = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile", stream=True)
                box = st.empty()
                full = ""
                for ch in stream:
                    if ch.choices[0].delta.content:
                        full += ch.choices[0].delta.content
                        box.markdown(full + "▌")
                
                if "[CHART_DATA]" in full:
                    clean = full.replace("[CHART_DATA]", "")
                    box.markdown(clean)
                    if "last_df" in st.session_state: st.line_chart(st.session_state.last_df)
                else: box.markdown(full)
                
                st.session_state.messages.append({"role": "assistant", "content": full})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
            except Exception as e: st.error(str(e))