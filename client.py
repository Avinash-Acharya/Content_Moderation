import gradio as gr
from scrape import scrape_content
from queuing import process_text_content, process_image_content
# from bs4 import BeautifulSoup
# from text_model import detect_hate_speech
# from image_model import detect_nsfw_image

def process_content(url):
    """
    Processes the content of a given URL by scraping and modifying its HTML structure.
    Args:
        url (str): The URL of the webpage to be processed.
    Yields:
        tuple: A tuple containing a status message and the current state of the HTML content.
            - "Error", content: If the content scraping fails.
            - "Processing text... (current/total)", html: During text processing, with the current state of the HTML.
            - "Processing images... (current/total)", html: During image processing, with the current state of the HTML.
            - "Processing complete", html: When all processing is complete, with the final HTML content.
    Notes:
        - Image sources are kept unchanged or processed as needed.
        - CSS styles and links are reattached to the <head> of the HTML.
        - The final HTML structure is returned with UTF-8 encoding.
    """

    content, soup = scrape_content(url)
    if soup is None:
        yield "Error", content
    # for style in content['styles']:
    #     soup.head.append(style)  
    # for link in content['css_links']:
    #     soup.head.append(link)  
    for i, text in enumerate(content['text']):
        # if not isinstance(text, str):
        #     continue
        processed_text = process_text_content(text)
        # processed_text = detect_hate_speech(text)
        element = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'a', 'li'])[i]
        # if processed_text.strip(): # Skip empty text
        if element.string:
            element.string.replace_with(processed_text)
        else:
            element.append(processed_text)
        yield f"Processing text... ({i+1}/{len(content['text'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8')

    for i, img_src in enumerate(content['images']):
        processed_image = process_image_content(img_src) 
        # processed_image = detect_nsfw_image(img_src) 
        soup.find_all('img')[i]['src'] = processed_image
        yield f"Processing images... ({i+1}/{len(content['images'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8')
    yield "Processing complete", soup.prettify(formatter='html').encode('utf-8').decode('utf-8')



# gradio interface
with gr.Blocks() as demo:
    url_input = gr.Textbox(label="Enter URL", placeholder="https://example.com")
    gr.Examples(
      examples=["https://hackaichallenge.devpost.com/", "https://devfolio.co/google-genaiexchange","https://nsfw-eg.vercel.app/"],
      inputs=url_input,
      label="Example URLs"
    )
    submit_btn = gr.Button("Analyze URL")
    status_output = gr.Label(label="Status")
    html_output = gr.HTML(label="Modified Webpage")
    submit_btn.click(process_content, inputs=url_input, outputs=[status_output, html_output])

demo.launch(debug=True)