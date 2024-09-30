import requests
from bs4 import BeautifulSoup


def extract_youtube_links(html_content):
    """
    Extracts YouTube video links from the provided HTML content.
    This function parses the given HTML content to find and extract YouTube video links.
    It looks for embedded YouTube videos within <iframe> tags and collects their URLs.
    Args:
        html_content (str): The HTML content to parse for YouTube links.
    Returns:
        list: A list of YouTube video URLs found in the HTML content.
    Example:
        html_content = '<html><body><iframe src="https://www.youtube.com/embed/example"></iframe></body></html>'
        links = extract_youtube_links(html_content)
        print(links)  # Output: ['https://www.youtube.com/embed/example']
    """

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
    """
    Retrieves YouTube links from the given URL.
    This function sends a GET request to the specified URL, retrieves the content,
    and extracts YouTube links from the response text. If the request fails, it raises
    a ValueError.
    Args:
        url (str): The URL from which to retrieve content.
    Returns:
        list: A list of YouTube links extracted from the URL content.
    Raises:
        ValueError: If the content retrieval from the URL fails.
    """

    print("- Retrieving content from URL...")
    response = requests.get(url)
    if response.status_code == 200:
        youtube_links = extract_youtube_links(response.text)
        return youtube_links
    else:
        raise ValueError(f"Failed to retrieve content from URL: {url}")