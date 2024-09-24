import gradio as gr
from scrape import scrape_content
from queuing import process_text_content, process_image_content

def process_content(url):

    content, soup = scrape_content(url)
    if soup is None:
        yield "Error", content

    for style in content['styles']:
        soup.head.append(style)  
    for link in content['css_links']:
        soup.head.append(link)  

    for i, text in enumerate(content['text']):
        processed_text = process_text_content(text)
        element = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'a', 'li'])[i]
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