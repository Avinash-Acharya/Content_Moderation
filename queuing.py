import re
import json
import queue
import threading
from video_model import fake_video_news
from image_model import detect_nsfw_image
from text_model import detect_hate_speech
from news_fakery import fake_news_detector
from ytlink import get_youtube_links_from_url

class Agent:
    """
    Agent class for processing text and image data concurrently.
    Attributes:
        text_queue (queue.Queue): Queue to hold text data for processing.
        image_queue (queue.Queue): Queue to hold image URLs for processing.
        processed_text (list): List to store processed text responses.
        processed_image (Any): Variable to store the processed image result.
        text_thread (threading.Thread): Thread for processing text data.
        image_thread (threading.Thread): Thread for processing image data.
    Methods:
        __init__(): Initializes the Agent with queues, processed data storage, and starts the processing threads.
        process_text(): Continuously processes text data from the text_queue, detects hate speech, and stores the result.
        process_image(): Continuously processes image URLs from the image_queue, detects NSFW content, and stores the result.
    """

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
    """
    Processes the given text content by splitting it into sentences and queuing them for further processing.
    This function detects hate speech by splitting the input text into sentences based on punctuation marks 
    (., !, ?, ;, :). Each sentence is then added to a queue for further processing by an agent. The processed 
    sentences are joined back into a single string and returned.
    Args:
        text (str): The input text content to be processed.
    Returns:
        str: The processed text content.
    """

    print("- Detecting hate speech...")
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
    """
    Processes an image URL by adding it to an image processing queue and waiting for the processing to complete.
    Args:
        url (str): The URL of the image to be processed. Must be a valid HTTP or HTTPS URL.
    Raises:
        ValueError: If the provided URL is not a string or does not start with 'http://' or 'https://'.
    Returns:
        processed_image: The processed image after it has been processed by the agent.
    """

    # print("BEFORE", url)
    if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid URL: {url}")
    agent.processed_image = None  
    agent.image_queue.put(url)
    agent.image_queue.join()  
    # print("AFTER",agent.processed_image)
    return agent.processed_image

def process_url_content(url):
    """
    Processes the content of a given URL to detect fake news in both articles and associated YouTube videos.
    This function first checks the article content at the given URL for fake news using the `fake_news_detector` function.
    If the article is not fake, it then retrieves YouTube links from the URL and checks each video for fake news using the `fake_video_news` function.
    Args:
        url (str): The URL of the article to be processed.
    Returns:
        dict: A dictionary containing the results of the fake news detection for the article and any associated YouTube videos.
              The dictionary has the following structure:
              {
                  "Article": <article_response_json>,
                  "Video": {
                      "Video 1 with URL <link1>": <video_response1>,
                      "Video 2 with URL <link2>": <video_response2>,
                      ...
                  }
              }
              If the article is fake, the "Video" key will not be present in the dictionary.
    """

    article_response = fake_news_detector(url)
    article_response_json = json.loads(article_response)
    combined_response = {"Article": article_response_json}

    if article_response_json['fake'] == False:
        ytlink_list = get_youtube_links_from_url(url)
        video_response = {}
        for i, link in enumerate(ytlink_list):
            response = fake_video_news(link)
            video_response[f"Video {i+1} with URL {link}"] = response

        combined_response["Video"] = video_response

    return combined_response

agent = Agent()