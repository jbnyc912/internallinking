import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64

def find_urls_with_keywords_and_target(site_urls, keywords, target_url):
    progress_bar = st.progress(0)
    passed_urls = []
    st.write("Crawling...")
    for i, url in enumerate(site_urls):
        st.write(f"Crawling {i+1} out of {len(site_urls)}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        keyword_found = False
        for keyword in keywords:
            if keyword.lower() in soup.get_text().lower():
                keyword_found = True
                passed_urls.append((url, keyword))
        progress_bar.progress(int((i+1)/len(site_urls)*100))
    st.write(f"Finished crawling {len(site_urls)} sites. Found {len(passed_urls)} internal linking opportunities.")
    return passed_urls

def main():
    st.title("Internal Linking Finder")
    st.markdown("---")
    site_urls = st.text_area("Site URLs", value="Paste URLs below, one per line", height=150)
    site_urls = site_urls.strip().split("\n")
    keywords = st.text_area("Keywords", value="Paste relevant keywords or terms below, one per line", height=150)
    keywords = keywords.strip().split("\n")
    target_url = st.text_input("Target URL", value="Target URL you're looking to add internal links to")
    if st.button("Run Crawler"):
        passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
        if passed_urls:
            # Export results to CSV
            data = {"URL": [url[0] for url in passed_urls], "Keyword": [url[1] for url in passed_urls]}
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="Internal Linking - {target_url}.csv"><button>Download CSV</button></a>'
            st.markdown(href, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**Finished crawling {len(site_urls)} sites. Found {len(passed_urls)} internal linking opportunities.**", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
