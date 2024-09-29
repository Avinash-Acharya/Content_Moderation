import requests
from bs4 import BeautifulSoup


def extract_youtube_links(html_content):

    print("- Extracting YouTube links...")
    soup = BeautifulSoup(html_content, 'html.parser')
    youtube_links = []

    # Find all YouTube video links
    # for link in soup.find_all('a', href=True):
    #     if 'youtube.com/watch' in link['href'] or 'youtu.be/' in link['href']:
    #         youtube_links.append(link['href'])

    # Find all embedded YouTube videos
    for iframe in soup.find_all('iframe'):
        if 'youtube.com/embed/' in iframe.get('src', ''):
            youtube_links.append(iframe['src'])

    return youtube_links

def get_youtube_links_from_url(url):

    print("- Retrieving content from URL...")
    response = requests.get(url)
    if response.status_code == 200:
        youtube_links = extract_youtube_links(response.text)
        return youtube_links
    else:
        raise ValueError(f"Failed to retrieve content from URL: {url}")