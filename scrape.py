import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from custom_css import DARK_THEME_CSS

def scrape_content(url):
    """
    Scrapes content from a given URL and processes it.
    This function fetches the HTML content from the specified URL, parses it using BeautifulSoup,
    and extracts text elements, image elements, and styles. It also converts relative image URLs
    to absolute URLs and appends a custom dark theme CSS to the HTML head.
    Args:
        url (str): The URL of the webpage to scrape.
    Returns:
        tuple: A tuple containing:
            - content (dict): A dictionary with the following keys:
                - 'text' (list): A list of text content from <p>, <h1>, <h2>, <h3>, <span>, <a>, and <li> elements.
                - 'images' (list): A list of absolute URLs of images.
                - 'styles' (ResultSet): A BeautifulSoup ResultSet of <style> elements.
                - 'css_links' (ResultSet): A BeautifulSoup ResultSet of <link> elements with rel="stylesheet".
            - soup (BeautifulSoup): The BeautifulSoup object of the parsed HTML content.
    Raises:
        requests.exceptions.RequestException: If there is an error fetching the content from the URL.
    """

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        styles = soup.find_all('style')
        css_links = soup.find_all('link', rel="stylesheet")
        custom_style_tag = soup.new_tag('style')
        custom_style_tag.string = DARK_THEME_CSS
        soup.head.append(custom_style_tag)
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'a', 'li'])
        image_elements = soup.find_all('img')
        # Convert relative image URLs to absolute URLs
        for img in image_elements:
            img_src = img.get('src')
            if img_src and not img_src.startswith(('http://', 'https://')):
                img['src'] = urljoin(url, img_src)  
        # Prepare content for processing
        content = {
            'text': [el.get_text() for el in text_elements],
            'images': [img['src'] for img in image_elements if img.get('src')],
            'styles': styles,
            'css_links': css_links
        }
        return content, soup
    except requests.exceptions.RequestException as e:
        return f"Error fetching the content from URL: {e}", None