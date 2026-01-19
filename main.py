import streamlit as st
from groq import Groq
import base64
import os
import pandas as pd
import PyPDF2
from dotenv import load_dotenv

# --- 1. SETUP ---
load_dotenv()
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = os.getenv("GROQ_API_KEY")
except:
    api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Gemini Pro Chat", page_icon="✨", layout="wide")

# --- 2. CSS STYLING (แก้บั๊กช่องพิมพ์) ---
st.markdown("""
<style>
    /* พื้นหลังขาวสะอาด */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    
    /* ซ่อน Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- ปุ่มแนบไฟล์ (Fixed Position) --- */
    /* แก้ไข: ใส่ width: fit-content เพื่อไม่ให้กล่องล่องหนไปบังช่องพิมพ์ */
    .stPopover {
        position: fixed;
        bottom: 80px;      /* อยู่เหนือช่องพิมพ์ */
        right: 30px;       /* ย้ายมาขวา (จะได้ไม่บัง User พิมพ์) */
        z-index: 9999;
        width: fit-content !important; /* สำคัญมาก! แก้บั๊กกดไม่ได้ */
    }
    
    /* แต่งปุ่มให้สวย */
    .stPopover button {
        background-color: #f0f4f9 !important;
        color: #444746 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .stPopover button:hover {
        background-color: #d3e3fd !important;
        color: #0b57d0 !important;
    }

    /* --- Chat Bubble --- */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }
    /* User Message */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e3f2fd; 
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 10px;
        border-bottom-right-radius: 5px;
    }
    /* Bot Message */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #ffffff;
        padding: 1rem;
    }
    
    /* ขยับช่องพิมพ์ให้สวยงาม */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_text_from_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- 4. HEADER & SETTINGS ---
col1, col2 = st.columns([9, 1])
with col1:
    st.caption("✨ Gemini Pro Clone")
with col2:
    with st.popover("⚙️", help="ตั้งค่า"):
        mode = st.radio("Mode", ["Smart", "Creative", "Coder"])
        if st.button("🗑️ Reset Chat", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# --- 5. LOGIC & UI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติแชท
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            content = msg["content"]
            if isinstance(content, list):
                for part in content:
                    if part["type"] == "text": st.markdown(part["text"])
                    if part["type"] == "image_url": st.image(part["image_url"]["url"], width=200)
            else:
                st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="✨"):
            st.markdown(msg["content"])

# --- ปุ่มแนบไฟล์ (Floating Widget) ---
# วางไว้ตรงนี้ แต่ CSS จะดีดมันไปมุมขวาล่าง
with st.popover("📎"):
    st.markdown("###### 📂 แนบไฟล์")
    uploaded_file = st.file_uploader(
        "Upload", 
        type=["pdf", "csv", "xlsx", "txt", "jpg", "png"],
        label_visibility="collapsed"
    )
    
    file_content = ""
    is_image = False
    
    if uploaded_file:
        st.success(f"✅ แนบ: {uploaded_file.name}")
        if "image" in uploaded_file.type:
            is_image = True
            st.image(uploaded_file, width=150)
        else:
            file_content = extract_text_from_file(uploaded_file)

# --- CHAT INPUT ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # 1. แสดง User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # 2. เตรียมข้อมูล
    user_msg_obj = prompt
    model_to_use = "llama-3.3-70b-versatile"
    
    # Context prompt
    system_prompt = "คุณคือ AI ผู้ช่วยอัจฉริยะ ตอบคำถามกระชับ ชัดเจน และช่วยเหลือผู้ใช้อย่างเต็มที่"
    if mode == "Creative": system_prompt = "คุณคือเพื่อนคู่คิดที่ความคิดสร้างสรรค์ เป็นกันเอง"
    if mode == "Coder": system_prompt = "คุณคือโปรแกรมเมอร์ผู้เชี่ยวชาญ ตอบด้วยโค้ด"

    # จัดการไฟล์แนบ
    if uploaded_file:
        if is_image:
            model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct"
            base64_img = encode_image(uploaded_file)
            user_msg_obj = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]
            st.session_state.messages.append({"role": "user", "content": user_msg_obj})
        else:
            system_prompt += f"\n\n[CONTEXT FROM FILE]:\n{file_content}\n\n[INSTRUCTION]: ตอบโดยอ้างอิงข้อมูลจากไฟล์"
            st.session_state.messages.append({"role": "user", "content": prompt})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. ส่ง API
    messages_payload = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[:-1]:
        c = m["content"]
        if isinstance(c, list):
            text_only = ""
            for p in c:
                if p["type"] == "text": text_only += p["text"]
            messages_payload.append({"role": m["role"], "content": text_only})
        else:
            messages_payload.append({"role": m["role"], "content": c})
    
    messages_payload.append({"role": "user", "content": user_msg_obj})

    # 4. รับผลลัพธ์ (ใส่ตัวแก้ภาษาต่างดาวให้แล้ว)
    with st.chat_message("assistant", avatar="✨"):
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=0.7,
                stream=True,
            )
            
            # Generator สำหรับแกะ Text ออกจาก JSON stream
            def parse_stream(stream):
                for chunk in stream:
                    if chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
            
            response = st.write_stream(parse_stream(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")