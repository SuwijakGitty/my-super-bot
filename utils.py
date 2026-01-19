import base64
import pandas as pd
import PyPDF2
from gtts import gTTS
import io
from groq import Groq  # ต้อง Import อันนี้ด้วย ไม่งั้นจะฟังไม่ได้

# --- 1. เครื่องมือจัดการไฟล์ ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            pdf = PyPDF2.PdfReader(uploaded_file)
            return "".join([p.extract_text() for p in pdf.pages])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except: return "อ่านไฟล์ไม่ได้"

def stream_parser(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- 2. ฟังก์ชัน "หูทิพย์" (Transcribe - ฟังเสียงคนพูด) ---
# 🔥 อันนี้แหละครับที่หายไป! ผมเอามาคืนให้แล้ว
def transcribe_audio(audio_bytes, api_key):
    try:
        client = Groq(api_key=api_key)
        # สร้างไฟล์เสียงจำลองในหน่วยความจำ
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav" # ตั้งชื่อสมมติให้มัน

        # ส่งไปให้ Groq ช่วยฟัง (Model: Whisper)
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3", # หูทิพย์ภาษาไทย
            language="th",
            response_format="text"
        )
        return transcription
    except Exception as e:
        return None

# --- 3. ฟังก์ชัน "ปากแจ๋ว" (TTS - พูดตอบกลับ) ---
def text_to_speech(text, lang='th'):
    try:
        # สร้างเสียงพูด (slow=False คือพูดเร็วปกติ)
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # บันทึกลง Memory
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        print(f"เกิดข้อผิดพลาดเสียง: {e}")
        return None