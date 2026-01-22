import streamlit as st
from groq import Groq
import uuid
import pandas as pd

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

# 3. Sidebar
with st.sidebar:
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=50)
        except: st.write("🛡️")
    with col_title:
        st.markdown("## XianBot")
    
    st.caption("🚀 Status: Stable (Llama 3.3)")
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
            if isinstance(content, list): content = "[Attached File]"
            chat_log += f"{role}: {content}\n{'-'*20}\n"
            
        st.download_button(
            label="💾 Save Chat",
            data=chat_log,
            file_name=f"chat_{st.session_state.session_id[:6]}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.markdown("---")
        st.caption("History")
        saved_chats = history.get_chat_history_list()
        for chat in saved_chats:
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                if st.button(chat["title"], key=chat["id"], use_container_width=True):
                    st.session_state.session_id = chat["id"]
                    st.session_state.messages = history.load_chat(chat["id"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"del_{chat['id']}"):
                    history.delete_chat(chat["id"])
                    st.rerun()

# ==========================================
# 🔥 MAIN LOGIC (Stable Version)
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
            msgs = [{"role": "system", "content": "คุณคือผู้ช่วย AI ภาษาไทย ตอบสั้นๆ กระชับ"}]
            for m in st.session_state.messages[-4:]:
                c = m.get("display", m["content"])
                if isinstance(c, str): msgs.append({"role": m["role"], "content": c})
            msgs.append({"role": "user", "content": transcript})
            try:
                # ใช้ Llama 3.3 70B (เสถียรสุด)
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
            except: st.markdown("# 🛡️")
        st.markdown(f"<h3 style='text-align: center; color: #666;'>XianBot Pro<br><span style='font-size: 0.6em; color: #28a745;'>Stable Edition (Llama 3.3)</span></h3>", unsafe_allow_html=True)

    # 1. แสดง Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="logo.png" if msg["role"] == "assistant" else None):
            d = msg.get("display", msg["content"])
            if isinstance(d, str) and "[CHART_DATA]" in d:
                if "last_df" in st.session_state:
                    st.line_chart(st.session_state.last_df)
                    st.caption("📊 กราฟวิเคราะห์ข้อมูล")
                d = d.replace("[CHART_DATA]", "")
            
            if isinstance(d, list): 
                for p in d:
                    if p["type"]=="text": st.markdown(p["text"])
                    if p["type"]=="image_url": st.image(p["image_url"]["url"], width=400)
            else: st.markdown(d)

    # 2. Upload File (Excel/PDF Only - รูปภาพปิดชั่วคราว)
    with st.container():
        uploaded_file = st.file_uploader("แนบไฟล์ (Excel / CSV / PDF)", 
                                       type=["pdf", "txt", "docx", "csv", "xlsx", "png", "jpg"], 
                                       label_visibility="collapsed")
        f_ctx, f_img = "", None
        
        if uploaded_file:
            # 🟡 ดักจับรูปภาพ (เพื่อแจ้งเตือนไม่ให้ Error)
            if "image" in uploaded_file.type:
                 st.warning("⚠️ ขออภัยครับ ระบบวิเคราะห์รูปภาพของ Groq ปิดปรับปรุงชั่วคราว (ใช้ได้เฉพาะ Text/Excel/PDF ครับ)", icon="🚧")
                 # ไม่เซ็ต f_img เพื่อป้องกันการเรียก Vision Model

            # 🟢 Excel/CSV
            elif "csv" in uploaded_file.type or "spreadsheet" in uploaded_file.type or "excel" in uploaded_file.type:
                try:
                    if "csv" in uploaded_file.name: df = pd.read_csv(uploaded_file)
                    else: df = pd.read_excel(uploaded_file)
                    
                    st.session_state.last_df = df.select_dtypes(include=['float', 'int'])
                    f_ctx = f"Data File '{uploaded_file.name}':\n{df.head(20).to_markdown()}"
                    st.toast(f"✅ อ่านไฟล์: {uploaded_file.name}")
                    with st.expander(f"🔎 ดูข้อมูล ({len(df)} แถว)"): st.dataframe(df)
                    
                except Exception as e: st.error(f"อ่านไฟล์ไม่ได้: {e}")
            
            # 🔵 เอกสาร
            else:
                f_ctx = utils.extract_file(uploaded_file)
                st.toast(f"✅ อ่านเอกสาร: {uploaded_file.name}")

    # 3. Chat Input
    prompt = st.chat_input("พิมพ์อะไรก็ได้... (Excel/PDF/Youtube พร้อม!)")

    if prompt:
        real_load = prompt
        disp_load = prompt
        
        # 1. YouTube
        if "youtube.com" in prompt or "youtu.be" in prompt:
            st.toast("กำลังแกะคลิป...", icon="📺")
            with st.spinner("Analyzing..."):
                transcript = utils.get_youtube_content(prompt, api_key)
                if transcript: real_load = f"สรุปคลิปนี้ (ไทย):\n\n{transcript}"
                else: st.error("แกะคลิปไม่ได้"); st.stop()

        # 2. Attachments
        elif f_ctx: 
            real_load = f"{prompt}\n\n---\n[File Context]:\n{f_ctx}"
            if "last_df" in st.session_state: real_load += "\n(Reply '[CHART_DATA]' if visualization is needed.)"

        st.session_state.messages.append({"role": "user", "content": real_load, "display": disp_load})
        st.rerun()

    # 4. AI Reply
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                msgs = [{"role": "system", "content": "คุณคือ XianBot ผู้ช่วยอัจฉริยะ ตอบภาษาไทยเสมอ"}]
                
                for m in st.session_state.messages[:-1]:
                    c = m.get("content")
                    if isinstance(c, str): 
                        msgs.append({"role": m["role"], "content": c})
                
                last = st.session_state.messages[-1]["content"]
                msgs.append({"role": "user", "content": last})
                
                # 🔥 ใช้โมเดล Llama 3.3 70B Versatile (ตัวเดียวจบ เสถียรสุด)
                model = "llama-3.3-70b-versatile" 

                stream = client.chat.completions.create(messages=msgs, model=model, stream=True)
                box = st.empty()
                full = ""
                for ch in stream:
                    if ch.choices[0].delta.content:
                        full += ch.choices[0].delta.content
                        box.markdown(full + "▌")
                
                if "[CHART_DATA]" in full:
                    clean_text = full.replace("[CHART_DATA]", "")
                    box.markdown(clean_text)
                    if "last_df" in st.session_state:
                        st.line_chart(st.session_state.last_df)
                        st.caption("📈 Generated Chart")
                else:
                    box.markdown(full)

                st.session_state.messages.append({"role": "assistant", "content": full})
                history.save_chat(st.session_state.session_id, st.session_state.messages)
            except Exception as e: st.error(f"Groq Error: {e}")