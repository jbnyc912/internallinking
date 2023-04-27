import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_sitemap(sitemap_url, keyword, target_url):
    sitemap = requests.get(sitemap_url)
    soup = BeautifulSoup(sitemap.content, 'html.parser')
    urls = [element.text for element in soup.findAll('loc')]
    matching_urls = []
    for url in urls:
        html_content = requests.get(url).content
        if keyword in html_content.decode('utf-8'):
            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a'):
                if link.get('href') == target_url:
                    break
            else:
                matching_urls.append(url)
    return matching_urls

st.title('Sitemap Scraper')

sitemap_url = st.text_input('Enter the URL of the sitemap:')
keyword = st.text_input('Enter a keyword to search for in the sitemap URLs:')
target_url = st.text_input('Enter the URL of the target site:')

if st.button('Search'):
    matching_urls = scrape_sitemap(sitemap_url, keyword, target_url)
    st.write(f'The following {len(matching_urls)} URLs match your search criteria:')
    for url in matching_urls:
        st.write(url)
