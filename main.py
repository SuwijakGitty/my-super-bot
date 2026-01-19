import streamlit as st
from groq import Groq
import uuid
import os

# Import Modules
import config
import styles
import utils
import history

# 1. Setup
config.setup_page()
styles.load_css()
api_key = config.get_api_key() # Groq API Key

# 🔥 ดึง Hugging Face Token มาเตรียมไว้
try:
    hf_api_token = st.secrets.get("HUGGINGFACE_API_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
except:
    hf_api_token = os.getenv("HUGGINGFACE_API_TOKEN")

# 2. Session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False
if "image_gen_mode" not in st.session_state:
    st.session_state.image_gen_mode = False

# 3. Sidebar (เหมือนเดิม)
with st.sidebar:
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        try: st.image("logo.png", width=60)
        except: st.write("🤖")
    with col_title:
        st.markdown("## XianBot")

    st.markdown("---")
    
    # สวิตช์โหมดวาดรูป
    if not st.session_state.voice_mode:
        is_img_mode = st.toggle("🎨 โหมดวาดรูป (Image Gen)", value=st.session_state.image_gen_mode)
        if is_img_mode != st.session_state.image_gen_mode:
            st.session_state.image_gen_mode = is_img_mode
            st.rerun()
            
    st.markdown("---")

    # ปุ่มสลับ Voice Mode
    if st.session_state.voice_mode:
        if st.button("💬 กลับไปหน้าแชท", type="primary", use_container_width=True):
            st.session_state.voice_mode = False
            st.rerun()
    else:
        if st.button("🎙️ เข้าโหมดเสียง (Voice Mode)", type="secondary", use_container_width=True):
            st.session_state.voice_mode = True
            st.session_state.image_gen_mode = False
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
# 🔥 MODE 1: VOICE MODE (เหมือนเดิม)
# ==========================================
if st.session_state.voice_mode:
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
# 🔥 MODE 2: CHAT & IMAGE GEN MODE
# ==========================================
else:
    # Welcome Screen
    if not st.session_state.messages:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try: st.image("logo.png", width=120, use_column_width=False, style={"display": "block", "margin-left": "auto", "margin-right": "auto"})
            except: st.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
            
            if st.session_state.image_gen_mode:
                 st.markdown("<h1 style='text-align: center; background: linear-gradient(to right, #ff00cc, #333399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>เข้าสู่โหมดวาดรูป 🎨</h1>", unsafe_allow_html=True)
                 st.info("💡 พิมพ์สิ่งที่อยากให้วาดได้เลย! (เช่น: แมวน่ารักใส่แว่นกันแดดบนชายหาด)")
            else:
                 st.markdown("<h1 style='text-align: center; background: linear-gradient(74deg, #4285f4 0%, #9b72cb 19%, #d96570 30%, #1f1f1f 60%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>XianBot พร้อม!</h1>", unsafe_allow_html=True)
        
        if not st.session_state.image_gen_mode:
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

    # Render Chat
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = None if role == "user" else "logo.png"
        with st.chat_message(role, avatar=avatar):
            if isinstance(msg["content"], list):
                for p in msg["content"]:
                    if p["type"]=="text": st.markdown(p["text"])
                    # 🔥 แสดงรูปภาพจาก base64
                    if p["type"]=="image_base64": 
                        st.image(f"data:image/png;base64,{p['image_base64']}", width=500) 
            else: 
                st.markdown(msg["content"])

    # File Upload
    with st.popover("📎", help="แนบไฟล์"):
        uploaded_file = st.file_uploader("Upload", label_visibility="collapsed")
        file_txt = utils.extract_file(uploaded_file) if uploaded_file and "image" not in uploaded_file.type else ""

    # Input Handling
    placeholder_text = "พิมพ์คำสั่งวาดรูปที่นี่... 🎨" if st.session_state.image_gen_mode else "พิมพ์ข้อความ / Type here... 😊"
    if prompt := st.chat_input(placeholder_text):
        
        # 🔥 1. กรณี: Image Gen Mode (วาดรูปด้วย Hugging Face)
        if st.session_state.image_gen_mode:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)
            
            with st.chat_message("assistant", avatar="logo.png"):
                with st.spinner("🎨 XianBot กำลังสะบัดแปรงวาดรูป... (ใช้เวลาสักครู่)"):
                    if not hf_api_token:
                         st.error("⚠️ ไม่พบ HUGGINGFACE_API_TOKEN กรุณาตั้งค่าใน .env หรือ Secrets")
                    else:
                        # เรียกใช้จิตรกรเทพ
                        img_base64 = utils.generate_image_huggingface(prompt, hf_api_token)
                        if img_base64:
                            # แสดงรูป
                            st.image(f"data:image/png;base64,{img_base64}", width=500, caption=f"Prompt: {prompt}")
                            # บันทึกลงประวัติ (เก็บเป็น base64)
                            st.session_state.messages.append({"role": "assistant", "content": [{"type": "text", "text": f"**วาดเสร็จแล้วครับ!** 🎨✨\n*Prompt: {prompt}*"}, {"type": "image_base64", "image_base64": img_base64}]})
                            history.save_chat(st.session_state.session_id, st.session_state.messages)
                        else:
                            st.error("เกิดข้อผิดพลาดในการวาดรูป ลองใหม่อีกครั้งนะครับ")
            st.rerun()

        # 2. กรณี: Chat Mode ปกติ
        else:
            user_content = prompt
            if uploaded_file:
                if "image" in uploaded_file.type:
                    img = utils.encode_image(uploaded_file)
                    user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]
            
            st.session_state.messages.append({"role": "user", "content": user_content})
            st.rerun()

    # Logic การตอบ (เฉพาะ Chat Mode)
    if not st.session_state.image_gen_mode and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        system_instruction = config.SYSTEM_PROMPT
        last_msg = st.session_state.messages[-1]
        if uploaded_file and "image" not in uploaded_file.type: system_instruction += f"\n\n[Context]: {file_txt}"

        with st.chat_message("assistant", avatar="logo.png"):
            try:
                client = Groq(api_key=api_key)
                msgs = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.messages[-10:-1]:
                    c = m["content"]
                    # 🔥 กรองเอาเฉพาะ text ไปส่ง AI (ไม่ส่งรูป base64)
                    if isinstance(c, list): c = "".join([x["text"] for x in c if x["type"]=="text"])
                    msgs.append({"role": m["role"], "content": c})
                msgs.append({"role": "user", "content": last_msg["content"]})
                
                model = "llama-3.3-70b-versatile"
                if isinstance(last_msg["content"], list): model = "meta-llama/llama-4-scout-17b-16e-instruct"

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