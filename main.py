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

st.set_page_config(page_title="AI Workspace", page_icon="✨", layout="wide")

# --- 2. CSS STYLING (แต่งหน้าตาให้เหมือน ChatGPT) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stChatMessage {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* ซ่อนปุ่มเมนูรกๆ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS (ตัวแกะไฟล์) ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.type
    try:
        if "pdf" in file_type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif "csv" in file_type:
            df = pd.read_csv(uploaded_file)
            return df.to_markdown(index=False)
        elif "excel" in file_type or "spreadsheet" in file_type:
            df = pd.read_excel(uploaded_file)
            return df.to_markdown(index=False)
        else: # txt, md, py, etc.
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- 4. SIDEBAR (เมนูควบคุม) ---
with st.sidebar:
    st.title("✨ AI Workspace")
    st.caption("Universal AI Assistant")
    
    # Mode Selection
    mode = st.selectbox("บุคลิก AI", [
        "🤖 ผู้ช่วยอัจฉริยะ (Smart)",
        "💻 โปรแกรมเมอร์ (Coder)",
        "📝 นักสรุปงาน (Summarizer)",
        "🔥 เพื่อนปากแจ๋ว (Roaster)"
    ])
    
    st.markdown("---")
    
    # Universal File Uploader
    st.subheader("📂 แนบไฟล์ (Documents/Images)")
    uploaded_file = st.file_uploader(
        "รองรับ PDF, Excel, CSV, TXT, JPG, PNG", 
        type=["pdf", "csv", "xlsx", "txt", "py", "md", "jpg", "png", "jpeg"]
    )
    
    # Preview File Content
    file_content = ""
    is_image = False
    
    if uploaded_file:
        file_type = uploaded_file.type
        if "image" in file_type:
            is_image = True
            st.image(uploaded_file, caption="Image Preview", use_container_width=True)
            st.success("✅ รูปภาพพร้อมวิเคราะห์")
        else:
            is_image = False
            with st.spinner("กำลังแกะเนื้อหาไฟล์..."):
                file_content = extract_text_from_file(uploaded_file)
                # ตัดข้อความถ้ายาวเกินไป (ป้องกัน Token เต็ม)
                if len(file_content) > 50000: 
                    file_content = file_content[:50000] + "...(truncated)"
                st.success(f"✅ อ่านไฟล์เรียบร้อย ({len(file_content)} ตัวอักษร)")
                with st.expander("ดูเนื้อหาไฟล์"):
                    st.text(file_content[:1000] + "...")

    st.markdown("---")
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown(f"### {mode}")

# Display History
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        content = msg["content"]
        if isinstance(content, list): # รูปภาพ
            for part in content:
                if part["type"] == "text": st.markdown(part["text"])
        else:
            st.markdown(content)

# Chat Input
if prompt := st.chat_input("พิมพ์คำถาม หรือสั่งให้สรุปไฟล์..."):
    # แสดงข้อความ User
    st.chat_message("user", avatar="👤").markdown(prompt)
    
    # เตรียมข้อมูลส่ง AI
    messages_payload = []
    
    # เลือก System Prompt ตามโหมด
    system_prompts = {
        "🤖 ผู้ช่วยอัจฉริยะ (Smart)": "คุณคือผู้ช่วยมืออาชีพ ตอบคำถามฉลาด กระชับ และถูกต้อง",
        "💻 โปรแกรมเมอร์ (Coder)": "คุณคือ Senior Developer ตอบด้วยโค้ดคุณภาพสูง อธิบาย Logic ชัดเจน",
        "📝 นักสรุปงาน (Summarizer)": "คุณคือผู้เชี่ยวชาญด้านการสรุปความ อ่านข้อมูลที่ได้รับแล้วสรุปใจความสำคัญเป็นข้อๆ",
        "🔥 เพื่อนปากแจ๋ว (Roaster)": "คุณคือเพื่อนปากแจ๋ว ขี้แซว พูดจาเป็นกันเอง (กู/มึง ได้) เน้นตลกและกวนประสาท"
    }
    
    # กรณีมีไฟล์เอกสาร (แนบเนื้อหาไปใน System Prompt เลยเพื่อให้ AI รู้เรื่องทั้งหมด)
    final_system_prompt = system_prompts[mode]
    if file_content:
        final_system_prompt += f"\n\n[CONTEXT FROM FILE]:\n{file_content}\n\n[INSTRUCTION]: ตอบคำถามโดยอ้างอิงข้อมูลจากไฟล์ด้านบนถ้าเกี่ยวข้อง"

    messages_payload.append({"role": "system", "content": final_system_prompt})

    # จัดการ Input
    if is_image and uploaded_file:
        # กรณีรูปภาพ -> ใช้ Vision Model
        model_to_use = "llama-3.2-11b-vision-preview" # ตัวนี้เสถียรสุดตอนนี้สำหรับฟรี
        base64_image = encode_image(uploaded_file)
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
        st.session_state.messages.append({"role": "user", "content": user_content})
    else:
        # กรณีข้อความ/เอกสาร -> ใช้ Text Model ตัวเทพ (Llama 3.3)
        model_to_use = "llama-3.3-70b-versatile"
        user_content = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})

    # รวม History (กรองเอาเฉพาะ Text เพื่อประหยัด Token)
    for m in st.session_state.messages[:-1]:
        content_str = m["content"]
        if isinstance(content_str, list):
            text_only = ""
            for part in content_str:
                if part["type"] == "text": text_only += part["text"]
            messages_payload.append({"role": m["role"], "content": text_only})
        else:
            messages_payload.append({"role": m["role"], "content": content_str})
    
    messages_payload.append({"role": "user", "content": user_content})

    # ส่งให้ AI
    with st.chat_message("assistant", avatar="🤖"):
        try:
            if not api_key:
                st.error("⚠️ ไม่พบ API Key")
                st.stop()

            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                messages=messages_payload,
                model=model_to_use,
                temperature=0.7,
                stream=True,
            )
            
            def parse_stream(stream):
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            response = st.write_stream(parse_stream(stream))
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")