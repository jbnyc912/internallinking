import requests
import streamlit as st
import xml.etree.ElementTree as ET

def scrape_sitemap(sitemap_url, target_url, keyword):
    sitemap = requests.get(sitemap_url)
    tree = ET.fromstring(sitemap.content)
    matching_urls = []
    for url in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        if keyword in requests.get(loc).text and target_url not in requests.get(loc).text:
            matching_urls.append(loc)
    return matching_urls

st.title('Sitemap Scraper')

sitemap_url = st.text_input('Enter the URL of the sitemap:')
target_url = st.text_input('Enter the URL of the target site:')
keyword = st.text_input('Enter a keyword to search for in the sitemap URLs:')

if st.button('Search'):
    matching_urls = scrape_sitemap(sitemap_url, target_url, keyword)
    st.write(f'The following {len(matching_urls)} URLs match your search criteria:')
    for url in matching_urls:
        st.write(url)
