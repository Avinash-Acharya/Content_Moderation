import os
import gradio as gr
from scrape import scrape_content
from queuing import process_text_content, process_image_content, process_url_content, process_audio_content

aud = None

def process_content(url, toggle_state1, toggle_state2):
    """
    Processes the content of a given URL, optionally generating an audio summary and analyzing news credibility.
    Args:
        url (str): The URL of the content to process.
        toggle_state1 (bool): Flag to indicate whether to analyze news credibility.
        toggle_state2 (bool): Flag to indicate whether to generate an audio summary.
    Yields:
        tuple: A tuple containing:
            - str: Status message indicating the current processing step.
            - str: The current state of the processed HTML content.
            - dict or None: The result of the news credibility analysis, if performed.
            - str or None: The path to the generated audio summary, if created.
    Notes:
        - The function scrapes the content from the given URL and processes text and images.
        - If `toggle_state1` is True, it analyzes the news credibility of the URL content.
        - If `toggle_state2` is True, it generates an audio summary of the URL content.
        - The function yields intermediate results at various stages of processing.
    """

    print("- Working on new URL...")
    global aud
    audio_summary = aud
    if audio_summary and os.path.exists(audio_summary):
        os.remove(audio_summary)
        audio_summary = None
    else:
        audio_summary = None
    json_result = None
    content, soup = scrape_content(url)
    if soup is None:
        yield "Error", content, json_result, audio_summary

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
            element = processed_text
        yield f"Processing text... ({i+1}/{len(content['text'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary

    for i, img_src in enumerate(content['images']):
        processed_image = process_image_content(img_src) 
        soup.find_all('img')[i]['src'] = processed_image
        yield f"Processing images... ({i+1}/{len(content['images'])})", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary

    toggledPrior2 = False
    if toggle_state2 and not toggledPrior2:
        yield "Generating audio summary...", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary
        audio_summary = process_audio_content(url)
        if audio_summary == "Content is too short to summarize. Less than 200 characters.":
            audio_summary = None
            print("Content is too short to summarize. Less than 200 characters.")
        aud = audio_summary
        toggledPrior2 = True
        yield "Audio Summary Generated", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary


    toggledPrior1 = False
    if toggle_state1 and not toggledPrior1:
        yield "Analyzing News Credibility...", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary
        json_result = process_url_content(url) 
        toggledPrior = True
        yield "News Credibility Analyzed", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary

        
    yield "Processing complete", soup.prettify(formatter='html').encode('utf-8').decode('utf-8'), json_result, audio_summary

  
# gradio interface
with gr.Blocks() as demo:
    url_input = gr.Textbox(label="Enter URL", placeholder="https://example.com")
    gr.Examples(
      examples=["https://nsfw-eg.vercel.app/", "https://www.nbcnews.com/health/health-news/fewer-1-5-large-companies-health-plans-cover-weight-loss-drugs-survey-rcna174345", "https://www.usatoday.com/story/entertainment/tv/2024/10/09/the-summit-tv-show-cbs/75560348007/"],
      inputs=url_input,
      label="Example URLs"
    )
    toggle_button1 = gr.Checkbox(label="Toggle to Analyse the Credibility of the article", value=False)
    toggle_button2 = gr.Checkbox(label="Toggle to Get an Audio Summary of this Page", value=False)
    submit_btn = gr.Button("Analyze URL")
    status_output = gr.Label(label="Status")
    json_output = gr.JSON(label="Article Credibility Analysis")
    audio_output = gr.Audio(label="Audio Summary")
    # audio_output = gr.Textbox(label="Audio Summary")
    html_output = gr.HTML(label="Modified Webpage")
    submit_btn.click(process_content, inputs=[url_input, toggle_button1, toggle_button2], outputs=[status_output, html_output, json_output, audio_output])

demo.launch(debug=True)