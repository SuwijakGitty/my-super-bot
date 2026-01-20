import base64
import pandas as pd
from gtts import gTTS
import io
from groq import Groq
import docx
import pdfplumber  # <-- พระเอกคนใหม่ของเรา!

# --- 1. เครื่องมือจัดการไฟล์ (ฉบับอัปเกรดภาษาไทย) ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        # 🔥 PDF: ใช้ pdfplumber แกะภาษาไทย (เทพกว่า PyPDF2 เยอะ!)
        if "pdf" in uploaded_file.type:
            with pdfplumber.open(uploaded_file) as pdf:
                # วนลูปอ่านทุกหน้าแล้วเอามาต่อกัน
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            return text
            
        # CSV
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
            
        # Excel
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
            
        # Word
        elif "docx" in uploaded_file.name or "word" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
            
        # Text File
        else:
            # ลองอ่านแบบ UTF-8 ก่อน ถ้าไม่ได้ให้ลอง TIS-620 (ภาษาไทยวินโดวส์เก่า)
            try:
                return uploaded_file.getvalue().decode("utf-8")
            except:
                return uploaded_file.getvalue().decode("tis-620")
                
    except Exception as e: 
        return f"อ่านไฟล์ไม่ได้ครับ: {e}"

# --- 2. ฟังก์ชัน "หูทิพย์" ---
def transcribe_audio(audio_bytes, api_key):
    try:
        client = Groq(api_key=api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3",
            language="th",
            response_format="text"
        )
        return transcription
    except Exception as e:
        return None

# --- 3. ฟังก์ชัน "ปากแจ๋ว" ---
def text_to_speech(text, lang='th'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        return None