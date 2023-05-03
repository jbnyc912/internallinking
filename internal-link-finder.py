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
        passed_urls.append({'URL': url, 'Keywords Found': keywords_on_page_str})
        num_passed += 1
        num_crawled += 1
        progress_text.text(f"Crawling {i+1} out of {len(site_urls)}...")
        progress_bar.progress(int((i+1)/len(site_urls)*100))
    return passed_urls

def main():
    st.set_page_config(page_title="Internal Linking Finder", page_icon=":link:")
    st.title("Internal Linking Finder")
    st.markdown("This tool allows you to identify URLs that don't currently link to the Target URL, and that mention the keyword(s).")

    # CSV upload
    st.subheader("Site URLs")
    st.markdown("*Upload a CSV file below. The list of URLs should be in column A with no header.*", unsafe_allow_html=True)
    st.markdown(
        """<style>
        .st-ca {
            margin-top: -10px;
        }
        </style>""", 
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("", type="csv")
    site_urls = []
    if uploaded_file is not None:
        site_urls = pd.read_csv(uploaded_file)
        site_urls = site_urls.iloc[:, 0].tolist()
        st.success(f"Found {len(site_urls)} URLs.")
    
    # Keywords
    st.subheader("Keywords")
    st.markdown("*Paste relevant keywords or terms below, one per line*", unsafe_allow_html=True)
    keywords = st.text_area("--", placeholder="blue widget\ngreen bicycle\norange balloon", height=150)
    keywords = keywords.split("\n")
    
    # Target URL
    st.subheader("Target URL")
    st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
    target_url = st.text_input("--", placeholder="www.example.com")
    
    if uploaded_file is None:
        if st.button("Find URLs"):
            site_urls = get_site_urls()
            st.success(f"Found {len(site_urls)} URLs.")
    
    if site_urls and keywords and target_url:
        # Run crawler
        if st.button("Run Crawler"):
            passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url)
            st.success(f"Finished crawling {len(site_urls)} URLs. Found {len(passed_urls)} internal linking opportunities.")
            if passed_urls:
                # Export results to CSV
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("**Export Results to CSV**")
                st.write("Click the button below to export results to CSV:")
                data = {'URL': [], 'Keywords Found': []}
                for url in passed_urls:
                    data['URL'].append(url['URL'])
                    data['Keywords Found'].append(url['Keywords Found'])
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                filename = f"Internal Linking - {target_url}.csv"
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}"><button>Download CSV</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("No URLs passed all checks.")

if __name__ == "__main__":
    main()
