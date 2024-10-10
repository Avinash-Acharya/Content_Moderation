import os
import re
import uuid
from summarizer import summarize
from urllib import request
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


load_dotenv()
VOICE_ID = "pFZP5JQG7iQjIQuC4Bku"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def load_content(url):
  """
  Loads the content from the given URL, extracts the text from the HTML, and returns the text.
  Args:
    url (str): The URL of the web page to load.
  Returns:
    str: The extracted text from the web page.
  Description:
    This function fetches the HTML content from the provided URL, parses it using BeautifulSoup, and extracts all the text within paragraph tags. 
    It concatenates the text from all paragraphs into a single string, removes any non-breaking space characters, and returns the resulting text. 
    If the extracted text is less than 200 characters, it returns a message indicating that the content is too short to summarize.
  """
  print("- Loading and summarizing the article...")
  html = request.urlopen(url).read().decode('utf8')
  soupObj = bs(html, "html.parser")
  paras = soupObj.find_all('p')
  allPara = " "
  for para in paras:
    allPara = allPara + para.text
  allPara = re.sub(r'\xa0', '', allPara) 
  if len(allPara) < 200:
    return "Content is too short to summarize. Less than 200 characters."
  return allPara

def elevenlabs_tts(text):
  """
  Converts the given text to speech using the Eleven Labs Text-to-Speech API and saves the output as an MP3 file.
  Args:
    text (str): The text to be converted to speech.
  Returns:
    str: The file path of the saved MP3 file.
  Description:
    This function uses the Eleven Labs Text-to-Speech API to convert the provided text into speech. 
    The speech is saved as an MP3 file with a unique filename generated using UUID. 
    The function prints the status of the conversion process and the location where the audio file is saved.
  """

  print("- Converting text to speech...")
  response = client.text_to_speech.convert(
        voice_id = VOICE_ID,  
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",  # or use `eleven_multilingual_v2` for multilingual support
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
  save_file_path = f"{uuid.uuid4()}.mp3"
  with open(save_file_path, "wb") as f:
      for chunk in response:
          if chunk:
              f.write(chunk)
  print(f"A new audio file was saved successfully at {save_file_path}")
  return save_file_path

def audio_summarize(url):
  content = load_content(url)
  if content == "Content is too short to summarize. Less than 200 characters.":
    return content
  summary = summarize(content)
  audio_path = elevenlabs_tts(summary)
  return audio_path