import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from custom_css import DARK_THEME_CSS

def scrape_content(url):

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