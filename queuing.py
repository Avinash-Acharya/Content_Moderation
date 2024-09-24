import re
import queue
import threading
from text_model import detect_hate_speech
from image_model import detect_nsfw_image

class Agent:
    def __init__(self):
        self.text_queue = queue.Queue()
        self.image_queue = queue.Queue()
        self.processed_text = []
        self.processed_image = None

        self.text_thread = threading.Thread(target=self.process_text, daemon=True)
        self.image_thread = threading.Thread(target=self.process_image, daemon=True)
        self.text_thread.start()
        self.image_thread.start()

    def process_text(self):
        while True:
            try:
                sentence = self.text_queue.get(timeout=1)
                respond_text = detect_hate_speech(sentence)
                self.processed_text.append(respond_text)  
                self.text_queue.task_done()
            except queue.Empty:
                continue

    def process_image(self):
        while True:
            try:
                img_url = self.image_queue.get(timeout=1)
                self.processed_image = detect_nsfw_image(img_url)
                self.image_queue.task_done()
            except queue.Empty:
                continue


def process_text_content(text):
    # print("BEFORE", text)
    splits = re.split(r'([.!?;:])', text)
    agent.processed_text.clear()
    sentence_buffer = ""
    for item in splits:
        if item:
            if item.strip() in ".!?;:":  
                sentence_buffer += item  
                agent.text_queue.put(sentence_buffer.strip())  
                sentence_buffer = ""  
            else:
                sentence_buffer = item  
    agent.text_queue.join()
    result = ' '.join(agent.processed_text)
    # print("AFTER",result)
    return result if result else text

def process_image_content(url):
    # print("BEFORE", url)
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid URL: {url}")
    agent.processed_image = None  
    agent.image_queue.put(url)
    agent.image_queue.join()  
    # print("AFTER",agent.processed_image)
    return agent.processed_image

agent = Agent()