# Import the necessary libraries
import streamlit as st
import requests
pip install lxml
from lxml import etree

# Define the Streamlit app
def app():
    # Set the title
    st.title("Web Scraper")
    
    # Define the input fields
    sitemap_url = st.text_input("Enter the sitemap.xml URL:")
    keyword = st.text_input("Enter the keyword to search for:")
    target_url = st.text_input("Enter the target URL to avoid:")
    
    # Define a function to scrape the URLs
    def scrape_urls(sitemap_url, keyword, target_url):
        # Get the sitemap
        res = requests.get(sitemap_url)
        root = etree.fromstring(res.content)
        
        # Get the URLs from the sitemap
        urls = [loc.text for loc in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        
        # Loop through the URLs
        for url in urls:
            # Get the HTML of the URL
            res = requests.get(url)
            if res.status_code == 200:
                # Check if the keyword is in the HTML
                if keyword in res.text:
                    # Check if the target URL is not in the HTML
                    if target_url not in res.text:
                        # Return the URL
                        return url
        
        # If no URL is found, return None
        return None
    
    # Define the output
    if st.button("Scrape"):
        url = scrape_urls(sitemap_url, keyword, target_url)
        
        if url:
            st.success(f"Found URL: {url}")
        else:
            st.warning("No URL found.")
