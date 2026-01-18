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

# --- 2. CSS STYLING (หัวใจสำคัญ) ---
st.markdown("""
<style>
    /* พื้นหลังขาวสะอาด */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }
    
    /* ซ่อน Header/Footer ของ Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- ปรับแต่งปุ่มแนบไฟล์ (Floating Action Button) --- */
    .stPopover {
        position: fixed;
        bottom: 70px; /* สูงจากขอบล่าง (เหนือช่องพิมพ์) */
        left: 15px;   /* ชิดซ้าย */
        z-index: 1000;
    }
    
    /* แต่งปุ่มคลิปให้กลมและใหญ่ กดง่าย */
    .stPopover button {
        background-color: #f0f4f9 !important;
        color: #444746 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        font-size: 24px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stPopover button:hover {
        background-color: #d3e3fd !important;
        color: #0b57d0 !important;
        transform: scale(1.1);
    }

    /* --- ปรับแต่ง Chat Bubble --- */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }
    /* ข้อความ User (สีเทาจางๆ มนๆ) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f2f2f2; 
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 10px;
    }
    
    /* ขยับช่องพิมพ์ให้หลบปุ่มแนบไฟล์ */
    .stChatInputContainer {
        padding-bottom: 20px;
        padding-left: 60px; /* เว้นที่ด้านซ้ายให้ปุ่มคลิป */
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

# --- 4. TOP BAR (แทน Sidebar) ---
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown("### ✨ Gemini Chat")
with col2:
    # ปุ่มตั้งค่า (Setting) แบบ Popover มุมขวาบน
    with st.popover("⚙️", help="ตั้งค่าบอท"):
        st.markdown("### 🤖 ตั้งค่านิสัย")
        mode = st.radio("เลือกโหมด", ["Smart (ฉลาด)", "Creative (ขี้เล่น)", "Coder (เขียนโปรแกรม)"])
        st.markdown("---")
        if st.button("🗑️ ล้างแชท (Reset)", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# --- 5. LOGIC & UI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดง Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            content = msg["content"]
            if isinstance(content, list):
                for part in content:
                    if part["type"] == "text": st.markdown(part["text"])
                    if part["type"] == "image_url": st.image(part["image_url"]["url"], width=250)
            else:
                st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="✨"):
            st.markdown(msg["content"])

# --- ปุ่มแนบไฟล์ (ลอยอยู่มุมซ้ายล่าง) ---
with st.popover("📎", help="แนบไฟล์"):
    st.markdown("###### 📂 แนบเอกสาร / รูปภาพ")
    uploaded_file = st.file_uploader(
        "Upload", 
        type=["pdf", "csv", "xlsx", "txt", "jpg", "png"],
        label_visibility="collapsed"
    )
    
    file_content = ""
    is_image = False
    
    if uploaded_file:
        st.success(f"✅ พร้อมส่ง: {uploaded_file.name}")
        if "image" in uploaded_file.type:
            is_image = True
            st.image(uploaded_file, width=150)
        else:
            file_content = extract_text_from_file(uploaded_file)

# --- ช่องพิมพ์ข้อความ ---
if prompt := st.chat_input("พิมพ์ข้อความ..."):
    # 1. แสดงข้อความ User
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # 2. เตรียม Context
    user_msg_obj = prompt
    model_to_use = "llama-3.3-70b-versatile"
    
    # System Prompt ตามโหมด
    system_prompts = {
        "Smart (ฉลาด)": "คุณคือ AI ผู้ช่วยที่ฉลาด ตอบกระชับ ตรงประเด็น สุภาพ",
        "Creative (ขี้เล่น)": "คุณคือเพื่อนคู่คิด เน้นความคิดสร้างสรรค์ เป็นกันเอง",
        "Coder (เขียนโปรแกรม)": "คุณคือโปรแกรมเมอร์มือโปร ตอบด้วยโค้ดและคำอธิบายทางเทคนิค"
    }
    base_prompt = system_prompts.get(mode, "คุณคือ AI ผู้ช่วย")
    
    if uploaded_file:
        if is_image:
            model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct" # Vision Model
            base64_img = encode_image(uploaded_file)
            user_msg_obj = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]
            st.session_state.messages.append({"role": "user", "content": user_msg_obj})
        else:
            base_prompt += f"\n\n[ข้อมูลจากไฟล์แนบ]:\n{file_content}\n\n[คำสั่ง]: ตอบคำถามโดยใช้ข้อมูลจากไฟล์ด้านบน"
            st.session_state.messages.append({"role": "user", "content": prompt})
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. เตรียมส่ง API
    messages_payload = [{"role": "system", "content": base_prompt}]
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

    # 4. เรียก AI และ **แกะกล่องข้อความ** (แก้บั๊กภาษาต่างดาว)
    with st.chat_message("assistant", avatar="✨"):
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=0.7,
                stream=True,
            )
            
            # --- ฟังก์ชันแกะกล่อง (สำคัญมาก!) ---
            def parse_stream(stream):
                for chunk in stream:
                    if chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
            # ----------------------------------
            
            response = st.write_stream(parse_stream(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {e}")