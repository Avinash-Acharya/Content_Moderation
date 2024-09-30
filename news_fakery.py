import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# config for gemini model for video transcription 
generation_config1 = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 100,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
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
model1 = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config1,
  system_instruction="user will provide a summarised version of an news article. Tell if it's factual or fake, and if it's factual, then tell if it's opiniated or not.",
)
chat_session1 = model1.start_chat()

# config for gemini model for news article fakery detection
generation_config2 = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
    required = ["fake", "article", "opinion"],
    properties = {
      "fake": content.Schema(
        type = content.Type.BOOLEAN,
      ),
      "article": content.Schema(
        type = content.Type.BOOLEAN,
      ),
      "opinion": content.Schema(
        type = content.Type.BOOLEAN,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model2 = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config2,
  system_instruction="tell if the given URL is an article (blog , news) or non article web page. And if it is an article, then tell if its fake , real or opinionated.",
)

chat_session2 = model2.start_chat()

def fake_news_detector(text):
    """
    Detects if the given news article text is fake or real.
    This function sends the provided text to a chat session for analysis
    and returns the result indicating whether the news article is fake or real.
    Args:
      text (str): The news article text to be analyzed.
    Returns:
      str: The result from the chat session indicating if the news is fake or real in JSON.
    """
    
    print("Detecting if the news article is fake or real...")
    response = chat_session2.send_message(text)
    result = response.text
    return result

def fake_video_detector(text):
    """
    Detects if the video described by the given text is fake or real.
    This function sends the provided text to a chat session for analysis and 
    returns the result indicating whether the video is fake or real.
    Args:
      text (str): The transcription of the video to be analyzed.
    Returns:
      str: The result from the chat session indicating if the video is fake or real in JSON.
    """
    
    print("Detecting if the video is fake or real...")
    response = chat_session1.send_message(text)
    result = response.text
    return result