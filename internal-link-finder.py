import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64


def find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    progress_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)
    start_time = time.time()
    for i, url in enumerate(site_urls):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        keyword_found = False
        link_to_target_found = False
        
        if xpath:
            content_element = soup.find(xpath)
            if content_element:
                content_text = content_element.get_text()
            else:
                content_text = ""
        else:
            content_text = soup.get_text()

        for keyword in keywords:
            if keyword.lower() in content_text.lower():
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
            if keyword.lower() in content_text.lower():
                keywords_on_page.append(keyword)
        keywords_on_page_str = ', '.join(keywords_on_page)
        passed_urls.append({'URL': url, 'Keywords Found': keywords_on_page_str})
        num_passed += 1
        num_crawled += 1
        progress_text.text(f"Crawling {i+1} out of {len(site_urls)}...")
        progress_bar.progress(int((i+1) / len(site_urls) * 100))
        
        # Estimate remaining time
        elapsed_time = time.time() - start_time
        avg_time_per_url = elapsed_time / num_crawled
        remaining_urls = len(site_urls) - num_crawled
        remaining_time = avg_time_per_url * remaining_urls
        status_text = f"Estimated time remaining: {remaining_time:.2f} seconds"
        st.text(status_text)
        
    return passed_urls

def main():
    st.set_page_config(page_title="Internal Linking Finder - a Break The Web tool", page_icon=":link:")
    st.image("https://cdn-icons-png.flaticon.com/128/3093/3093852.png", width=40)
    st.title("Internal Linking Finder")
    st.markdown('*Created by [Break The Web](https://breaktheweb.agency)*')
    st.markdown("This tool allows you to identify URLs not currently linking to the Target URL, and also include the keyword(s)")

    # CSV upload
    st.subheader("Site URLs")
    st.markdown("*First, upload the list of URLs you would like to check in a CSV file with the URLs in column A and no header*", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="csv")
    if uploaded_file is not None:
        site_urls = pd.read_csv(uploaded_file)
        site_urls = site_urls.iloc[:, 0].tolist()
        st.success(f"Found {len(site_urls)} URLs.")

        # Keywords
        st.subheader("Keywords")
        st.markdown("*Paste relevant keywords or terms below, one per line*", unsafe_allow_html=True)
        keywords = st.text_area("", placeholder="payday loans\nonline casino\ncbd vape pen", height=150)
        keywords = keywords.split("\n")
        
        # XPath for Content Sections
        st.subheader("Content Section's Full XPath *(Optional)*")
        st.markdown("*By pasting in the full XPath of the content section, we can avoid looking at sitewide sections for internal links.*", unsafe_allow_html=True)
        xpath = st.text_input("", placeholder="")
                    
        # Target URL
        st.subheader("Target URL")
        st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
        target_url = st.text_input("", placeholder="https://breaktheweb.agency/seo/seo-timeline")

        # Run crawler
        if uploaded_file and keywords and target_url:
            if st.button("Run Crawler"):
                passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath)
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
