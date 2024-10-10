import os
import json
import time
import torch
import whisper
import subprocess
from summarizer import summarize
from news_fakery import fake_video_detector
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# S2T_MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
# SUM_MODEL_ID = "Falconsai/text_summarization"

device = "cuda" if torch.cuda.is_available() else "cpu"
# Stokenizer = AutoTokenizer.from_pretrained(SUM_MODEL_ID)
# Smodel = AutoModelForSeq2SeqLM.from_pretrained(SUM_MODEL_ID)
model = whisper.load_model("base").to(device)
# Smodel.to(device)

def download_audio(url, output_file, max_duration=100):
    """
    Downloads audio from a given YouTube URL and saves it as an MP3 file.
    Parameters:
    url (str): The URL of the YouTube video to download audio from.
    output_file (str): The path where the downloaded audio file will be saved.
    max_duration (int, optional): The maximum duration of the audio to download in seconds. Defaults to 100 seconds.
    Returns:
    None
    """

    print("- Downloading audio...")
    # subprocess.run(["echo", "- Downloading audio..."])
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
    """
    Transcribes the given audio file into text.
    Args:
        audio_file (str): The path to the audio file to be transcribed.
    Returns:
        str: The transcribed text from the audio file.
    """

    # start_time = time.time()
    print("- Transcribing audio...")
    # subprocess.run(["echo", "- Transcribing audio..."])
    result = model.transcribe(audio_file)
    # end_time = time.time()
    # time_taken = end_time - start_time
    # print(f"Transcribed text: {result["text"]}")
    # print(f"Time taken to Transcribe: {time_taken:.2f} seconds")
    return result["text"]  

def summarize_text(text):
    """
    Summarizes the given text using a summarization model.
    Args:
        text (str): The text to be summarized.
    Returns:
        str: The summarized version of the input text.
    """

    print("- Summarizing text...")
    # input_ids = Stokenizer(text, return_tensors="pt")
    # outputs = Smodel.generate(**input_ids, max_length=100, min_length=40)
    # summarized = Stokenizer.decode(outputs[0], skip_special_tokens=True)
    summarized = summarize(text)
    return summarized

def fake_video_news(url):
    """
    Processes a video from a given URL to detect fake news.
    This function performs the following steps:
    1. Downloads the audio from the video at the specified URL.
    2. Transcribes the downloaded audio to text.
    3. Summarizes the transcribed text.
    4. Detects whether the summarized text contains fake news.
    5. Optionally deletes the downloaded audio file after processing.
    Args:
        url (str): The URL of the video to be processed.
    Returns:
        dict: A dictionary containing the results of the fake news detection, 
              e.g., {"is_factual": bool, "is_opinionated": bool}.
    Raises:
        Exception: If any of the processing steps fail.
    Example:
        result = fake_video_news("https://example.com/video")
        print(result)
    """

    print("- Processing video...")
    start_time = time.time()
    output_file = "./audio.mp3"
    delete_after_process = True 

    download_audio(url, output_file)
    transcript = transcribe_audio(output_file)
    summary = summarize_text(transcript)
    result = fake_video_detector(summary)

    if delete_after_process and os.path.exists(output_file):
        os.remove(output_file)
        print(f"File {output_file} has been deleted.")

    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken to analyze: {time_taken:.2f} seconds")
    return result

