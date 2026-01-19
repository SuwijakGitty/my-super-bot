import base64
import pandas as pd
import PyPDF2
from gtts import gTTS
import io
from groq import Groq
# 🔥 เรียกใช้ไลบรารีใหม่
from huggingface_hub import InferenceClient
import os

# --- 1. เครื่องมือจัดการไฟล์ (เหมือนเดิม) ---
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

# --- 2. ฟังก์ชัน "หูทิพย์" (เหมือนเดิม) ---
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

# --- 3. ฟังก์ชัน "ปากแจ๋ว" (เหมือนเดิม) ---
def text_to_speech(text, lang='th'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        return None

# --- 4. 🔥 ฟังก์ชัน "จิตรกรเทพ (Hugging Face)" 🔥 ---
def generate_image_huggingface(prompt, api_token):
    """สร้างรูปภาพโดยใช้ Hugging Face Inference API (Stable Diffusion XL)"""
    try:
        # ใช้โมเดลฟรีตัวเทพ
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        client = InferenceClient(model=model_id, token=api_token)

        # เรียกให้วาดรูป
        image = client.text_to_image(prompt)
        
        # แปลงรูปภาพที่ได้เป็นรหัส base64 เพื่อส่งกลับไปแสดง
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return img_str
    except Exception as e:
        print(f"Hugging Face Error: {e}")
        return None