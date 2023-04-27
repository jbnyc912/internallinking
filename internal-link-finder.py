import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64

def find_urls_with_keywords_and_target(site_urls, keywords, target_url):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    progress_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)
    for i, url in enumerate(site_urls):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        keyword_found = False
        for keyword in keywords:
            if keyword.lower() in soup.get_text().lower():
                keyword_found = True
                break
        if not keyword_found:
            continue
        for link in soup.find_all("a"):
            href = link.get("href")
            if href is not None and (target_url in href or href.startswith(target_url)):
                passed_urls.append(url)
                num_passed += 1
                break
        num_crawled += 1
        progress_text.text(f"Crawling {i+1} out of {len(site_urls)}...")
        progress_bar.progress(int((i+1)/len(site_urls)*100))
    return passed_urls, num_passed


def main():
    st.title("**Internal Linking Finder**")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("**Site URLs**")
    st.markdown("*Paste URLs below, one per line*", unsafe_allow_html=True)
    site_urls = st.text_area("", placeholder="https://www.google.com\nhttps://www.github.com", height=150)
    site_urls = site_urls.split("\n")
    st.subheader("**Keywords**")
    st.markdown("*Paste relevant keywords or terms below, one per line*", unsafe_allow_html=True)
    keywords = st.text_area("", placeholder="blue widget\ngreen bicycle\norange balloon", height=150)
    keywords = keywords.split("\n")
    st.subheader("**Target URL**")
    st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
    target_url = st.text_input("", placeholder="https://www.example.com")
    if st.button("Run Crawler"):
        passed_urls, num_passed = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
        st.success(f"Finished crawling {len(site_urls)} sites. Found {num_passed} internal linking opportunities.")
        if passed_urls:
            st.warning("No URLs passed all checks.")

if __name__ == "__main__":
    main()
