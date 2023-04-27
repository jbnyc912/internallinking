import importlib
import streamlit as st
import requests
from bs4 import BeautifulSoup

# Check if bs4 is installed
if importlib.util.find_spec("bs4") is None:
    # If bs4 is not installed, install it
    !pip install bs4

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
        soup = BeautifulSoup(res.content, "xml")
        
        # Get the URLs from the sitemap
        urls = [loc.text for loc in soup.find_all("loc")]
        
        # Loop through the URLs
        for url in urls:
            # Get the HTML of the URL
            res = requests.get(url)
            soup = BeautifulSoup(res.content, "html.parser")
            
            # Check if the keyword is in the HTML
            if keyword in soup.text:
                # Check if the target URL is not in the HTML
                if target_url not in [a.get("href") for a in soup.find_all("a")]:
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
