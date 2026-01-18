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

st.set_page_config(page_title="Gemini Clone", page_icon="✨", layout="wide")

# --- 2. GEMINI STYLE CSS (หัวใจสำคัญ) ---
st.markdown("""
<style>
    /* 1. พื้นหลังขาว คลีนๆ */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    
    /* 2. ซ่อน Header รกๆ */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* 3. ปุ่มแนบไฟล์ (เทคนิคลอยปุ่ม Fixed Position) */
    /* จูนตำแหน่งให้ปุ่ม Clip ลอยอยู่เหนือช่องพิมพ์ด้านซ้าย */
    .stPopover {
        position: fixed;
        bottom: 80px; /* สูงจากพื้น 80px (เหนือช่องพิมพ์พอดี) */
        left: 20px;
        z-index: 9999; /* อยู่บนสุด */
    }
    
    /* แต่งปุ่ม Clip ให้สวยเหมือน Gemini */
    .stPopover button {
        background-color: #f0f4f9;
        color: #444746;
        border: none;
        border-radius: 50%; /* กลมดิก */
        width: 50px;
        height: 50px;
        font-size: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        transition: 0.2s;
    }
    .stPopover button:hover {
        background-color: #d3e3fd;
        color: #0b57d0;
    }

    /* 4. แต่งกล่องข้อความ */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }
    /* ข้อความ User (สีฟ้าจางๆ) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f0f4f9; 
        border-radius: 20px;
        padding: 10px;
    }
    
    /* 5. ปรับช่องพิมพ์ข้อความ */
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

# --- 4. SIDEBAR (ซ่อนไว้ เก็บแค่ Setting) ---
with st.sidebar:
    st.title("✨ Settings")
    mode = st.radio("Mode", ["Smart", "Creative", "Coder"], horizontal=True)
    if st.button("🗑️ Reset Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- 5. LOGIC & UI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title แบบ Gemini
st.markdown("## ✨ สวัสดีครับ มีอะไรให้ช่วยไหม?")

# --- ส่วนแสดงผล Chat History ---
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

# --- ปุ่มแนบไฟล์ (Floating Popover) ---
# วางไว้ตรงนี้ แต่ CSS จะสั่งให้มัน "ลอย" ไปอยู่ที่มุมซ้ายล่างเอง
with st.popover("📎", help="แนบไฟล์/รูปภาพ"):
    st.markdown("### 📂 แนบไฟล์")
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

# --- ช่องพิมพ์ข้อความ (Chat Input) ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # 1. แสดง User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # 2. เตรียมข้อมูล
    user_msg_obj = prompt
    model_to_use = "llama-3.3-70b-versatile" # Default Text
    
    system_prompt = "คุณคือ AI Assistant สไตล์ Gemini: ตอบกระชับ ฉลาด ทันสมัย และช่วยเหลือผู้ใช้อย่างเต็มที่"
    
    # กรณีแนบไฟล์
    if uploaded_file:
        if is_image:
            model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct" # Vision
            base64_img = encode_image(uploaded_file)
            user_msg_obj = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]
            st.session_state.messages.append({"role": "user", "content": user_msg_obj})
        else:
            # แนบเอกสาร Text/PDF
            system_prompt += f"\n\n[DOCUMENT CONTENT]:\n{file_content}\n\n[INSTRUCTION]: ตอบคำถามโดยอ้างอิงข้อมูลในเอกสารนี้"
            st.session_state.messages.append({"role": "user", "content": prompt})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. เตรียม Context ส่ง API
    messages_payload = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[:-1]:
        # Clean history object (กรองเอาแต่ text)
        c = m["content"]
        if isinstance(c, list): 
            text_only = ""
            for p in c:
                if p["type"] == "text": text_only += p["text"]
            messages_payload.append({"role": m["role"], "content": text_only})
        else:
            messages_payload.append({"role": m["role"], "content": c})
            
    messages_payload.append({"role": "user", "content": user_msg_obj})

    # 4. เรียก AI
    with st.chat_message("assistant", avatar="✨"):
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=0.7,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")