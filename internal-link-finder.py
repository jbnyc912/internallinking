import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64


def find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath=None):
    passed_urls = []
    num_crawled = 0
    num_passed = 0
    progress_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)
    for url in site_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        keyword_found = False
        link_to_target_found = False

        if xpath is not None and xpath.strip() != "":
            selected_elements = soup.select(xpath)
        else:
            selected_elements = [soup]

        for element in selected_elements:
            text = element.get_text()
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    keyword_found = True
                    break

            if keyword_found:
                break

            for link in element.find_all('a'):
                if link.has_attr('href') and target_url in link['href']:
                    link_to_target_found = True
                    break

            if link_to_target_found:
                break

        if not keyword_found and not link_to_target_found:
            keywords_on_page = [keyword for keyword in keywords if keyword.lower() in text.lower()]
            keywords_on_page_str = ', '.join(keywords_on_page)
            passed_urls.append({'URL': url, 'Keywords Found': keywords_on_page_str})

    return passed_urls


def main():
    st.set_page_config(page_title="Internal Linking Finder - a Break The Web tool", page_icon=":link:")
    st.image(
        "https://scontent.fslc3-2.fna.fbcdn.net/v/t39.30808-6/306042676_506308304831092_90216115740552247_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=1fBuPeS-wTYAX9JSC05&_nc_ht=scontent.fslc3-2.fna&oh=00_AfAnvRo-0PBoKFOsSv_Lt8vbWf2gOz5kwvHEjlkd0GlM2Q&oe=6457BA63",
        width=40)
    st.title("Internal Linking Finder")
    st.markdown("This tool allows you to identify URLs not currently linking to the Target URL, and also include the keyword(s)")

    # CSV upload
    st.subheader("Site URLs")
    st.markdown("*First, upload the list of URLs you would like to check in a CSV file with the URLs in column A and no header*",
                unsafe_allow_html=True)
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

        # XPath
        st.subheader("XPath (Optional)")
        st.markdown("*Provide an XPath expression to select specific elements for keyword and target URL search (e.g., //div[@class='content'])",unsafe_allow_html=True)
        xpath = st.text_input("XPath")

        # Target URL
        st.subheader("Target URL")
        st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
        target_url = st.text_input("", placeholder="https://breaktheweb.agency/seo/seo-timeline")

        # Run crawler
        if uploaded_file and keywords and target_url:
            if st.button("Run Crawler"):
                if xpath.strip() == "":
                    xpath = None
                passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath)
                st.success(
                    f"Finished crawling {len(site_urls)} URLs. Found {len(passed_urls)} internal linking opportunities.")
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

