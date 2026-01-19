import base64
import pandas as pd
import PyPDF2
# 🔥 เพิ่ม imports สำหรับระบบเสียง
from gtts import gTTS
import io
from groq import Groq

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

# --- 🔥 ฟังก์ชันใหม่สำหรับเสียง ---

def transcribe_audio(audio_bytes, api_key):
    """แปลงเสียงที่อัดมาเป็นข้อความ (ใช้ Groq Whisper)"""
    try:
        client = Groq(api_key=api_key)
        # สร้างไฟล์เสียงจำลองในหน่วยความจำ
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav" # ตั้งชื่อสมมติให้มัน

        # ส่งไปให้ Groq ช่วยฟัง
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3", # โมเดลหูทิพย์ของ Groq (ฟรี!)
            language="th", # บังคับให้ฟังเป็นภาษาไทย
            response_format="text"
        )
        return transcription
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการฟัง: {e}"

def text_to_speech(text, lang='th'):
    """แปลงข้อความกลับเป็นเสียงพูด (ใช้ Google TTS)"""
    try:
        # สร้างเสียงจากข้อความ
        tts = gTTS(text=text, lang=lang, slow=False)
        # บันทึกลงหน่วยความจำ (ไม่ต้องสร้างไฟล์จริง)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0) # เตรียมพร้อมเล่น
        return audio_fp
    except Exception as e:
        print(f"TTS Error: {e}")
        return None