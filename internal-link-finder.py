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
        link_to_target_found = False
        for keyword in keywords:
            if keyword.lower() in soup.get_text().lower():
                keyword_found = True
                break
        if not keyword_found:
            continue
        for link in soup.find_all('a'):
            if link.has_attr('href') and target_url in link['href']:
                link_to_target_found = True
                break
        if link_to_target_found:
            continue
        keywords_on_page = []
        for keyword in keywords:
            if keyword.lower() in soup.get_text().lower():
                keywords_on_page.append(keyword)
        keywords_on_page_str = ', '.join(keywords_on_page)
        passed_urls.append({'URL not linking to Target': url, 'Keywords Found': keywords_on_page_str})
        num_passed += 1
        num_crawled += 1
        progress_text.text(f"Crawling {i+1} out of {len(site_urls)}...")
        progress_bar.progress(int((i+1)/len(site_urls)*100))
    return passed_urls

def main():
    st.set_page_config(page_title="Internal Linking Finder", page_icon=":link:")
    st.title("Internal Linking Finder")
    st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod nunc ut orci rutrum, id vulputate odio ullamcorper. Praesent nec tellus augue.")
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Site URLs")
    st.markdown("*Paste URLs below, one per line*", unsafe_allow_html=True)
    site_urls = st.text_area("", placeholder="https://www.google.com\nhttps://www.github.com", height=150)
    site_urls = site_urls.split("\n")
    st.subheader("Keywords")
    st.markdown("*Paste relevant keywords or terms below, one per line*", unsafe_allow_html=True)
    keywords = st.text_area("", placeholder="blue widget\ngreen bicycle\norange balloon", height=150)
    keywords = keywords.split("\n")
    st.subheader("Target URL")
    st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
    target_url = st.text_input("", placeholder="www.example.com")
    if st.button("Run Crawler"):
        passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
        st.success(f"Finished crawling {len(site_urls)} sites. Found {len(passed_urls)} internal linking opportunities.")
        if passed_urls:
            # Export results to CSV
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Export Results to CSV")
            st.write("Click the button below to export results to CSV:")
            data = {'URL not linking to Target': [], 'Keywords Found': []}
            for url in passed_urls:
                data['URL not linking to Target'].append(url['URL'].replace("https://", "").replace("http://", "").replace("www.", ""))
                data['Keywords Found'].append(url['Keywords Found'])
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            filename = f"Internal Linking - {target_url.replace('https://', '').replace('http://', '').replace('www.', '')}.csv"
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}"><button>Download CSV</button></a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("No URLs passed all checks.")


if __name__ == "__main__":
    main()
