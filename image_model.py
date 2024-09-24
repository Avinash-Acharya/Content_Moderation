import torch
import requests
from PIL import Image
from io import BytesIO
from transformers import AutoModelForImageClassification, ViTImageProcessor

# cat = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTeKOOpLy92UjzQxq8NCxgxOQJbj_YVdfHO_g&s"
cat = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
MODEL = "Falconsai/nsfw_image_detection"

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = AutoModelForImageClassification.from_pretrained(MODEL)
processor = ViTImageProcessor.from_pretrained(MODEL)
model.to(device)

def detect_nsfw_image(url):
    """
    Detects whether an image from a given URL is NSFW (Not Safe For Work) or normal.
    Args:
        url (str): The URL of the image to be analyzed.
    Returns:
        str: The original URL if the image is normal, or a placeholder string if the image is NSFW.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        PIL.UnidentifiedImageError: If the image cannot be opened and identified.
        torch.TorchException: If there is an issue with the PyTorch model inference.
    """

    response = requests.get(url)
    if url.endswith(".svg") or response.status_code != 200:
        return url
    else:
        img = Image.open(BytesIO(response.content)).convert("RGB")

    with torch.no_grad():
        inputs = processor(images=img, return_tensors="pt")
        outputs = model(**inputs.to(device))
        logits = outputs.logits

    predicted_label = logits.argmax(-1).item()
    label = model.config.id2label[predicted_label]
    if label == "nsfw":
        return cat
    elif label == "normal":
        return url

# url = "https://www.nvidia.com/content/dam/en-zz/Solutions/gpu-cloud/ngc-enterprise-cloud-services-2c50-d.jpg"