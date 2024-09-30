import os
import json
import time
import torch
import librosa
import subprocess
from news_fakery import fake_video_detector
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor , AutoTokenizer, AutoModelForSeq2SeqLM

S2T_MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
SUM_MODEL_ID = "Falconsai/text_summarization"

device = "cuda" if torch.cuda.is_available() else "cpu"
Stokenizer = AutoTokenizer.from_pretrained(SUM_MODEL_ID)
Smodel = AutoModelForSeq2SeqLM.from_pretrained(SUM_MODEL_ID)
processor = Wav2Vec2Processor.from_pretrained(S2T_MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(S2T_MODEL_ID)
Smodel.to(device)
model.to(device)

def download_audio(url, output_file, max_duration=60):
    """
    Downloads the audio from a given YouTube URL and saves it as an MP3 file.
    This function uses the yt-dlp tool to download the audio from a YouTube video.
    It first retrieves the video information to determine the duration of the video.
    The audio is then downloaded and saved as an MP3 file, with an optional maximum duration limit.
    Args:
        url (str): The URL of the YouTube video to download the audio from.
        output_file (str): The path where the downloaded audio file will be saved.
        max_duration (int, optional): The maximum duration (in seconds) of the audio to download. Defaults to 60 seconds.
    Raises:
        subprocess.CalledProcessError: If the yt-dlp command fails.
        json.JSONDecodeError: If the video information cannot be parsed.
    Example:
        download_audio("https://www.youtube.com/watch?v=example", "output.mp3", max_duration=30)
    """

    print("- Downloading audio...")
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
    This function loads an audio file, processes it using a pre-trained model, 
    and returns the transcribed text. It uses the `librosa` library to load 
    the audio data and a pre-trained model for transcription.
    Args:
        audio_file (str): Path to the audio file to be transcribed.
    Returns:
        str: The transcribed text from the audio file.
    """

    print("- Transcribing audio...")
    audio_data, _ = librosa.load(audio_file, sr=16000)
    inputs = processor(audio_data, sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentence = processor.decode(predicted_ids[0])
    return predicted_sentence  

def summarize_text(text):
    """
    Summarizes the given text using a pre-trained language model.
    Args:
        text (str): The text to be summarized.
    Returns:
        str: The summarized version of the input text.
    Note:
        This function uses a tokenizer (Stokenizer) and a model (Smodel) 
        to generate the summary. The tokenizer converts the input text 
        into tokens, and the model generates the summary based on these tokens.
        The summary length is controlled by the max_length and min_length parameters.
    """
    
    print("- Summarizing text...")
    input_ids = Stokenizer(text, return_tensors="pt")
    outputs = Smodel.generate(**input_ids, max_length=100, min_length=40)
    summarized = Stokenizer.decode(outputs[0], skip_special_tokens=True)
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
    # transcript = download_audio(url, output_file)
    summary = summarize_text(transcript)
    result = fake_video_detector(summary)

    if delete_after_process and os.path.exists(output_file):
        os.remove(output_file)
        print(f"File {output_file} has been deleted.")

    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken: {time_taken:.2f} seconds")
    # print(result)
    # {"is_factual": false, "is_opinionated": false}
    return result

# url = "https://www.youtube.com/watch?v=ieK1PTXmopE&pp=ygUKb25pb24gbmV3cw%3D%3D"