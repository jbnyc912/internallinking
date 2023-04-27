import streamlit as st
import requests
from lxml import etree

def app():
    st.title("Web Scraper")

    sitemap_url = st.text_input("Enter the sitemap.xml URL:")
    keyword = st.text_input("Enter the keyword to search for:")
    target_url = st.text_input("Enter the target URL to avoid:")

    def scrape_urls(sitemap_url, keyword, target_url):
        res = requests.get(sitemap_url)
        root = etree.fromstring(res.content)
        urls = [loc.text for loc in root.xpath(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]

        for url in urls:
            res = requests.get(url)
            root = etree.fromstring(res.content)
            if keyword in root.xpath(".//body//text()"):
                if target_url not in root.xpath(".//a/@href"):
                    return url

        return None

    if st.button("Scrape"):
        url = scrape_urls(sitemap_url, keyword, target_url)

        if url:
            st.success(f"Found URL: {url}")
        else:
            st.warning("No URL found.")
