import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64


def find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    progress_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)
    for i, url in enumerate(site_urls, selector, target_url):
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException:
            # Handle the exception (e.g., skip URL or display an error message)
            continue
        soup = BeautifulSoup(response.content, "html.parser")
        if selector:
            selected_elements = soup.select(selector)
            if not selected_elements:
                continue
            selected_html = "\n".join([str(element) for element in selected_elements])
            soup = BeautifulSoup(selected_html, "html.parser")
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
    st.set_page_config(page_title="Internal Linking Finder - a Break The Web tool", page_icon=":link:")
    st.image("https://scontent.fslc3-2.fna.fbcdn.net/v/t39.30808-6/306042676_506308304831092_90216115740552247_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=1fBuPeS-wTYAX9JSC05&_nc_ht=scontent.fslc3-2.fna&oh=00_AfAnvRo-0PBoKFOsSv_Lt8vbWf2gOz5kwvHEjlkd0GlM2Q&oe=6457BA63", width=40)
    st.title("Internal Linking Finder")
    st.markdown("This tool allows you to identify URLs not current linking to the Target URL, and also include the keyword(s)")

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
        
        # Selector
        st.subheader("HTML Selector")
        st.markdown("*Optional: Enter an HTML selector to narrow down the crawl scope*", unsafe_allow_html=True)
        selector = st.text_input("", placeholder="Enter HTML selector (e.g., .content)")


        # Target URL
        st.subheader("Target URL")
        st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
        target_url = st.text_input("", placeholder="https://breaktheweb.agency/seo/seo-timeline")

        # Run crawler
        if uploaded_file and keywords and target_url:
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
