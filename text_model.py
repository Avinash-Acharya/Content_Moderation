import os
import json
import torch
from dotenv import load_dotenv
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from transformers import AutoTokenizer, AutoModelForSequenceClassification

load_dotenv()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# location = "../finetuned_text_model"
location = "facebook/roberta-hate-speech-dynabench-r4-target"
HFtokenizer = AutoTokenizer.from_pretrained(location)
HFmodel = AutoModelForSequenceClassification.from_pretrained(location)
HFmodel.to(device)
# Config for gemini model
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 500,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
    required = ["positive"],
    properties = {
      "positive": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="user will provide a inappropriate/hate-speech sentence and you need to convert it into the positive version, which is just one sentence long. Make sure the same pronoun is preserved.",
)
chat_session = model.start_chat()

def detect_hate_speech(text):

    if not text:
        return text
    inputs = HFtokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = HFmodel(**inputs.to(device)).logits
    predicted_class_id = logits.argmax().item()
    predicted_label = HFmodel.config.id2label[predicted_class_id]
    if predicted_label == "nothate":
        return text
    elif predicted_label == "hate":
        replaced_text = hate_speech_replacer(text)
        return replaced_text

def hate_speech_replacer(text):

    response = chat_session.send_message(text)
    response_json = json.loads(response.text)
    return response_json['positive']