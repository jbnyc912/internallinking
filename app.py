import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def check_url(url, keyword, target_url):
    try:
        # Get the HTML content of the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if the HTML contains the keyword
        if keyword not in soup.get_text():
            return None
        
        # Check if the HTML contains a link to the target URL
        parsed_target_url = urlparse(target_url)
        for link in soup.find_all('a'):
            parsed_link = urlparse(link.get('href'))
            if parsed_target_url.netloc == parsed_link.netloc and parsed_target_url.path == parsed_link.path:
                return None
        
        # If the URL passes all checks, return it
        return url
    
    except Exception as e:
        print(f"Error checking URL {url}: {e}")
        return None

def search_sitemap(sitemap_url, keyword, target_url):
    # Get the XML sitemap
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'xml')

    # Find all the URL tags in the sitemap
    urls = soup.find_all('url')

    # Check each URL for the keyword and target URL
    results = []
    for url in urls:
        loc = url.find('loc').text
        result = check_url(loc, keyword, target_url)
        if result:
            results.append(result)
    
    return results

# Example usage
sitemap_url = 'https://example.com/sitemap.xml'
keyword = 'example'
target_url = 'https://example.com/page-to-exclude'
results = search_sitemap(sitemap_url, keyword, target_url)
print(results)
