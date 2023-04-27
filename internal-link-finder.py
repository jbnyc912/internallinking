import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64


def find_urls_with_keywords_and_target(site_urls, keywords, target_url, progress_bar):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    for url in site_urls:
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
        progress_bar.progress(num_crawled/len(site_urls))
    return passed_urls, num_passed


def main():
    st.set_page_config(page_title="Internal Linking Finder", page_icon=":link:")

    st.title("**Internal Linking Finder**")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("**Site URLs**")
    st.markdown("*Paste URLs below, one per line*", unsafe_allow_html=True)
    site_urls = st.text_area("", "https://www.google.com\nhttps://www.github.com", height=75)
    site_urls = site_urls.split("\n")
    st.subheader("**Keywords**")
    st.markdown("*Paste relevant keywords or terms below, one per line*", unsafe_allow_html=True)
    keywords = st.text_area("", "Python\nStreamlit\nWeb scraping", height=150)
    keywords = keywords.split("\n")
    st.subheader("**Target URL**")
    st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
    target_url = st.text_input("", "https://www.example.com")
    if st.button("Run Crawler"):
        passed_urls, num_passed = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
        st.success(f"Finished crawling {len(site_urls)} sites. Found {num_passed} internal linking opportunities.")
        if passed_urls:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("**URLs that passed all checks**")
            for passed_url in passed_urls:
                st.write(passed_url)
            
            # Export results to CSV
            st.markdown("<br>", unsafe_allow_html=True)
            data = {"URL": passed_urls, "Keyword": [", ".join(keywords)] * len(passed_urls)}
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="results.csv"><button>Download CSV</button></a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("No URLs passed all checks.")



if __name__ == "__main__":
    main()
