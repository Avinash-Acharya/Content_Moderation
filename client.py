import gradio as gr
# import concurrent.futures
from scrape import scrape_content
from queuing import process_text_content, process_image_content, process_url_content

def process_content(url, toggle_state):
    """
    Processes the content of a given URL, optionally toggling additional processing.
    This function scrapes content from the provided URL, processes text and image elements,
    and yields intermediate results at various stages of processing. If `toggle_state` is True,
    additional processing is performed on the URL content.
    Args:
        url (str): The URL of the content to be processed.
        toggle_state (bool): A flag to toggle additional processing.
    Yields:
        tuple: A tuple containing a status message (str), the current state of the HTML content (str),
               and a JSON result (dict or None).
    Notes:
        - The function processes text and images sequentially.
        - If `toggle_state` is True, additional processing is performed on the URL content.
        - The function uses BeautifulSoup to manipulate HTML content.
    """

    json_result = None
    content, soup = scrape_content(url)
    if soup is None:
        yield "Error", content, json_result

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
            # element.append(processed_text)
            element = processed_text
        yield f"Processing text... ({i+1}/{len(content['text'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result

    for i, img_src in enumerate(content['images']):
        processed_image = process_image_content(img_src) 
        soup.find_all('img')[i]['src'] = processed_image
        yield f"Processing images... ({i+1}/{len(content['images'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result

    ## The below code is for parallel processing of text and images

    # def process_text(i, text):
    #     print("text :", text," i :",i)
    #     processed_text = process_text_content(text)
    #     print("processed_text :", processed_text)
    #     element = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'a', 'li'])[i]
    #     if element.string:
    #         element.string.replace_with(processed_text)
    #     else:
    #         element.append(processed_text)
    #     return f"Processed text... ({i+1}/{len(content['text'])})"

    # def process_image(i, img_src):
    #     processed_image = process_image_content(img_src)
    #     soup.find_all('img')[i]['src'] = processed_image
    #     return f"Processed image... ({i+1}/{len(content['images'])})"

    # # Process text and images in parallel
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     text_futures = {executor.submit(process_text, i, text): i for i, text in enumerate(content['text'])}
    #     image_futures = {executor.submit(process_image, i, img_src): i for i, img_src in enumerate(content['images'])}

    #     for future in concurrent.futures.as_completed(text_futures):
    #         yield future.result(), soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result
        
    #     for future in concurrent.futures.as_completed(image_futures):
    #         yield future.result(), soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result

    toggledPrior = False
    if toggle_state and not toggledPrior:
        result = process_url_content(url) 
        json_result = result
        toggledPrior = True
        
        
    yield "Processing complete", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result

# gradio interface
with gr.Blocks() as demo:
    url_input = gr.Textbox(label="Enter URL", placeholder="https://example.com")
    gr.Examples(
      examples=["https://nsfw-eg.vercel.app/"],
      inputs=url_input,
      label="Example URLs"
    )
    toggle_button = gr.Checkbox(label="Toggle to Analyse the Credibility of the article", value=False)
    submit_btn = gr.Button("Analyze URL")
    json_output = gr.JSON(label="Article Credibility Analysis")
    status_output = gr.Label(label="Status")
    html_output = gr.HTML(label="Modified Webpage")
    submit_btn.click(process_content, inputs=[url_input, toggle_button], outputs=[status_output, html_output, json_output])

demo.launch(debug=True)