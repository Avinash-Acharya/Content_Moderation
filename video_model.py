import os
import json
import time
import torch
import librosa
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor , AutoTokenizer, AutoModelForSeq2SeqLM

load_dotenv()
S2T_MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
SUM_MODEL_ID = "Falconsai/text_summarization"
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


device = "cuda" if torch.cuda.is_available() else "cpu"
Stokenizer = AutoTokenizer.from_pretrained(SUM_MODEL_ID)
Smodel = AutoModelForSeq2SeqLM.from_pretrained(SUM_MODEL_ID)
processor = Wav2Vec2Processor.from_pretrained(S2T_MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(S2T_MODEL_ID)
Smodel.to(device)
model.to(device)

# config for gemini model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 100,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = "[]",
    required = ["is_factual", "is_opinionated"],
    properties = {
      "is_factual": content.Schema(
        type = content.Type.BOOLEAN,
      ),
      "is_opinionated": content.Schema(
        type = content.Type.BOOLEAN,
      ),
    },
  ),
  "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="user will provide a summarised version of an news article. Tell if it's factual or fake, and if it's factual, then tell if it's opiniated or not.",
)
chat_session = model.start_chat()

def download_audio(url, output_file, max_duration=60):
    
    result = subprocess.run(
        ["yt-dlp", "--skip-download", "--print-json", url],
        stdout=subprocess.PIPE, text=True
    )
    video_info = json.loads(result.stdout)
    duration = video_info["duration"]  
    download_duration = min(max_duration, duration)
    subprocess.run([
        "yt-dlp", url,
        "-x", "--audio-format", "mp3",
        f"--postprocessor-args=-ss 00:00:00 -t {download_duration}",
        "-o", output_file
    ])

def transcribe_audio(audio_file):
    
    audio_data, _ = librosa.load(audio_file, sr=16000)
    inputs = processor(audio_data, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentence = processor.decode(predicted_ids[0])
    return predicted_sentence

def summarize_text(text):
        
    input_ids = Stokenizer(text, return_tensors="pt")
    outputs = model.generate(**input_ids, max_length=100, min_length=40)
    summarized = Stokenizer.decode(outputs[0], skip_special_tokens=True)
    return summarized

def fake_news_detector(text):
    
    response = chat_session.send_message(text)
    result = response.text
    return result

def fake_video_news(url = "https://www.youtube.com/watch?v=ieK1PTXmopE&pp=ygUKb25pb24gbmV3cw%3D%3D"):
    
    start_time = time.time()

    output_file = "./audio_files/audio.mp3"
    delete_after_process = True 

    download_audio(url, output_file)
    transcript = transcribe_audio(output_file)
    summary = summarize_text(transcript)
    result = fake_news_detector(summary)

    if delete_after_process and os.path.exists(output_file):
        os.remove(output_file)
        print(f"File {output_file} has been deleted.")

    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken: {time_taken:.2f} seconds")

    return result