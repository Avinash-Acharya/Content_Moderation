import queue
import threading
from flask import Flask, request, jsonify
from text_model import detect_hate_speech
from image_model import detect_nsfw_image

app = Flask(__name__)

class Agent:
    def __init__(self):
        self.text_queue = queue.Queue()
        self.image_queue = queue.Queue()
        self.shutdown_flag = threading.Event()

        # Start the worker threads
        self.text_thread = threading.Thread(target=self.process_text_queue, daemon=True)
        self.image_thread = threading.Thread(target=self.process_image_queue, daemon=True)
        self.text_thread.start()
        self.image_thread.start()

    def process_text_queue(self):
        while not self.shutdown_flag.is_set():
            try:
                sentence = self.text_queue.get(timeout=1)
                respond_text = detect_hate_speech(sentence)
                print(f"Processed text: {respond_text}")
                self.text_queue.task_done()
            except queue.Empty:
                continue

    def process_image_queue(self):
        while not self.shutdown_flag.is_set():
            try:
                image = self.image_queue.get(timeout=1)
                respond_image = detect_nsfw_image(image)
                print(f"Processed image: {respond_image}")
                self.image_queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self.shutdown_flag.set()

# Create an agent instance with loaded models
agent = Agent()

@app.route('/process/text', methods=['POST'])
def process_text_content():
    content = request.get_json()
    sentences = content['text'].split('. ')
    for sentence in sentences:
        agent.text_queue.put(sentence)
    return jsonify({'status': 'Text processing started'}), 202
    # return Response(text_stream(sentences), content_type='text/event-stream')

@app.route('/process/image', methods=['POST'])
def process_image_content():
    content = request.get_json()
    images = content['images']  # Assuming multiple images are sent in a list
    agent.image_queue.put(images)
    return jsonify({'status': 'Image processing started'}), 202
    # return Response(image_stream(images), content_type='text/event-stream')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    agent.stop()
    return jsonify({'status': 'Shutting down agent...'}), 200

if __name__ == '__main__':
    app.run(debug=True)
