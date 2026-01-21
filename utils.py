import base64
import pandas as pd
from gtts import gTTS
import io
from groq import Groq
import docx
import pdfplumber
from youtube_transcript_api import YouTubeTranscriptApi
import re
import yt_dlp
import os

# --- 1. เครื่องมือจัดการไฟล์ ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_file(uploaded_file):
    try:
        if "pdf" in uploaded_file.type:
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif "csv" in uploaded_file.type:
            return pd.read_csv(uploaded_file).to_markdown(index=False)
        elif "excel" in uploaded_file.type or "spreadsheet" in uploaded_file.type:
            return pd.read_excel(uploaded_file).to_markdown(index=False)
        elif "docx" in uploaded_file.name or "word" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            try: return uploaded_file.getvalue().decode("utf-8")
            except: return uploaded_file.getvalue().decode("tis-620")
    except Exception as e: return f"อ่านไฟล์ไม่ได้ครับ: {e}"

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
    except: return None

# --- 3. ฟังก์ชัน "ปากแจ๋ว" (TTS) ---
def text_to_speech(text, lang='th'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except: return None

# --- 4. ฟังก์ชันดูดคลิป (YouTube) ---
def get_youtube_content(url, api_key):
    metadata_text = ""
    # พยายามดึงชื่อคลิป
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'ไม่ระบุชื่อคลิป')
            channel_name = info.get('uploader', 'ไม่ระบุชื่อช่อง')
            metadata_text = f"📌 ข้อมูลคลิป:\n- ชื่อคลิป: {video_title}\n- เจ้าของช่อง: {channel_name}\n\n"
    except: pass

    # วิธี 1: ลองดึงซับไตเติ้ล
    try:
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id:
            transcript = YouTubeTranscriptApi.get_transcript(video_id.group(1), languages=['th', 'en'])
            text = " ".join([t['text'] for t in transcript])
            return f"{metadata_text}📜 (แกะจากซับ):\n{text[:15000]}"
    except: pass 

    # วิธี 2: ถ้าไม่มีซับ ให้โหลดเสียงมาแกะ (ใช้ FFmpeg)
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],
            'ffmpeg_location': '.', 
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists('temp_audio.mp3'):
            client = Groq(api_key=api_key)
            with open('temp_audio.mp3', 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=('temp_audio.mp3', audio_file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            os.remove('temp_audio.mp3')
            return f"{metadata_text}🎧 (แกะจากเสียง):\n{transcription}"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการแกะคลิป: {e}"
    
    return None