import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64

def reset_fields():
    uploaded_file = None
    site_urls = []
    keywords = []
    selector = ""
    target_url = ""

def find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    progress_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)
    for i, url in enumerate(site_urls):
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
    st.image("https://cdn-icons-png.flaticon.com/128/9841/9841627.png", width=40)
    st.title("Internal Linking Finder")
    st.markdown("This tool allows you to identify URLs not current linking to the Target URL, and also include the keyword(s)")

    # CSV upload
    st.subheader("Site URLs")
    st.write("*First, upload the list of URLs you would like to check in a CSV file with the URLs in column A and no header*")
    
    uploaded_file = st.file_uploader("", type="csv")
    if uploaded_file is not None:
        site_urls = pd.read_csv(uploaded_file)
        site_urls = site_urls.iloc[:, 0].tolist()
        st.success(f"Found {len(site_urls)} URLs.")

        # Keywords
        st.subheader("Keywords")
        st.write("*Paste relevant keywords or terms below, one per line*")
        keywords = st.text_area("", placeholder="payday loans\nonline casino\ncbd vape pen", height=150)
        keywords = keywords.split("\n")
        
        # Selector
        st.subheader("HTML Selector")
        st.write("*Optional: Enter an HTML selector to narrow down the crawl scope & avoid sitewide elements*")
        selector = st.text_input("", placeholder="Enter HTML selector (e.g., .content)")


        # Target URL
        st.subheader("Target URL")
        st.write("*Target URL you're looking to add internal links to*")
        target_url = st.text_input("", placeholder="https://breaktheweb.agency/seo/seo-timeline")

        # Run crawler
        if uploaded_file and keywords and target_url:
            if st.button("Run Crawler"):
                crawl_started = True  # Set crawl_started to True
                with st.spinner("Crawling in progress... be patient"):
                    passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector)
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

                # Show balloons when crawl is complete
                st.balloons()

                # Reset button
                if st.button("Reset"):
                    reset_fields()

                
if __name__ == "__main__":
    main()
