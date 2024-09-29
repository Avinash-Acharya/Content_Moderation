from flask_cors import CORS
from flask import Flask, request, jsonify
from queuing import process_image_content, process_text_content, process_url_content

app = Flask(__name__)
CORS(app)


@app.route('/process/text', methods=['POST'])
def process_text():
    content = request.get_json()
    sentences = content['text']
    response = process_text_content(sentences)
    return jsonify(response), 200

@app.route('/process/image', methods=['POST'])
def process_image():
    content = request.get_json()
    images = content['images']  
    response = process_image_content(images)
    return jsonify(response), 200

@app.route('/process/url', methods=['POST'])
def process_url():
    content = request.get_json()
    url = content['url']
    response = process_url_content(url)
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)

