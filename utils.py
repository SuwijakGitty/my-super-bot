import base64
import pandas as pd
import PyPDF2
from gtts import gTTS
import io
from groq import Groq
import docx  # <-- เรียกใช้ไลบรารีอ่าน Word

# --- 1. เครื่องมือจัดการไฟล์ ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        # กรณีไฟล์ PDF
        if "pdf" in uploaded_file.type:
            pdf = PyPDF2.PdfReader(uploaded_file)
            return "".join([p.extract_text() for p in pdf.pages])
        
        # กรณีไฟล์ CSV
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        
        # กรณีไฟล์ Excel
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
            
        # 🔥 กรณีไฟล์ Word (.docx) - เพิ่มใหม่ตรงนี้!
        elif "docx" in uploaded_file.name or "word" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
            
        # กรณีไฟล์ Text ทั่วไป
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e: 
        return f"อ่านไฟล์ไม่ได้ครับ: {e}"

# --- 2. ฟังก์ชัน "หูทิพย์" (Transcribe) ---
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

# --- 3. ฟังก์ชัน "ปากแจ๋ว" (TTS) ---
def text_to_speech(text, lang='th'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        return None