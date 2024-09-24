import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from custom_css import DARK_THEME_CSS

# Function to scrape web content with UTF-8 encoding
def scrape_content(url):
    """
    Scrapes content from the given URL.
    This function fetches the HTML content from the specified URL, parses it using BeautifulSoup, 
    and extracts text and image elements. It also ensures that the request handles UTF-8 encoding 
    and converts relative image URLs to absolute URLs. Additionally, it adds custom CSS for a dark 
    background and white text to the parsed HTML.
    Args:
        url (str): The URL of the webpage to scrape.
    Returns:
        tuple: A tuple containing:
            - content (dict): A dictionary with the following keys:
                - 'text' (list): A list of text elements (paragraphs, headers, spans).
                - 'images' (list): A list of absolute URLs of images.
                - 'styles' (list): A list of <style> tags found in the <head>.
                - 'css_links' (list): A list of <link> tags with rel="stylesheet" found in the <head>.
            - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML.
    Raises:
        requests.exceptions.RequestException: If there is an error fetching the content from the URL.
    """

    try:
        # Ensure the request handles UTF-8
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Parse the content using BeautifulSoup with UTF-8 encoding
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        # Extract the <style> and <link> tags from the <head>
        styles = soup.find_all('style')
        css_links = soup.find_all('link', rel="stylesheet")
        # Add custom CSS for dark background and white text
        custom_style_tag = soup.new_tag('style')
        custom_style_tag.string = DARK_THEME_CSS
        soup.head.append(custom_style_tag)
        # Extract text and images from the body
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'span', 'a', 'li'])
        image_elements = soup.find_all('img')
        # Convert relative image URLs to absolute URLs
        for img in image_elements:
            img_src = img.get('src')
            if img_src and not img_src.startswith(('http://', 'https://')):
                img['src'] = urljoin(url, img_src)  # Convert to absolute URL
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