import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64

def find_urls_with_keywords_and_target(site_urls, keywords, target_url):
    st.write("Crawling...")
    passed_urls = []
    for i, url in enumerate(site_urls):
        st.write(f"Crawling {i+1} out of {len(site_urls)}")
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
                break
    st.write(f"There are {len(passed_urls)} internal linking opportunities.")
    return passed_urls

def main():
    st.set_page_config(page_title="Internal Linking Finder", page_icon=":link:")

    st.title("Internal Linking Finder")
    st.markdown("***")
    
    site_urls = st.text_area("Site URLs\n\n_Paste URLs below, one per line_")
    site_urls = site_urls.split("\n")
    
    keywords = st.text_area("Keywords\n\n_Paste relevant keywords or terms below, one per line_")
    keywords = keywords.split("\n")
    
    target_url = st.text_input("Target URL\n\n_Target URL you're looking to add internal links to_")
    
    if st.button("Run Crawler"):
        passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
        if passed_urls:
            st.write(f"Download {len(passed_urls)} internal linking opportunities as CSV:")
            data = {"URL": passed_urls, "Keyword": [", ".join(keywords)] * len(passed_urls)}
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="results.csv"><button>Download CSV</button></a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No URLs passed all checks.")

if __name__ == "__main__":
    main()
