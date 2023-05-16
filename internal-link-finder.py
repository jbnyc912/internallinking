import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64


def find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector=None):
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

        if selector is not None:
            selected_elements = soup.select(selector)
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
    st.image("https://scontent.fslc3-2.fna.fbcdn.net/v/t39.30808-6/306042676_506308304831092_90216115740552247_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=1fBuPeS-wTYAX9JSC05&_nc_ht=scontent.fslc3-2.fna&oh=00_AfAnvRo-0PBoKFOsSv_Lt8vbWf2gOz5kwvHEjlkd0GlM2Q&oe=6457BA63", width=40)
    st.title("Internal Linking Finder")
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

        # Target URL
        st.subheader("Target URL")
        st.markdown("*Target URL you're looking to add internal links to*", unsafe_allow_html=True)
        target_url = st.text_input("", placeholder="https://breaktheweb.agency/seo/
                                   
        # Selector
        st.subheader("Selector (Optional)")
        st.markdown("*If you want to target specific HTML elements, enter a CSS selector below*", unsafe_allow_html=True)
        selector = st.text_input("", placeholder="e.g., #main-content .article-body")

        # Run the analysis
        if st.button("Analyze"):
            if len(site_urls) == 0:
                st.warning("Please upload a CSV file with site URLs.")
            elif len(keywords) == 0:
                st.warning("Please enter at least one keyword.")
            elif len(target_url) == 0:
                st.warning("Please enter a target URL.")
            else:
                passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector)
                if len(passed_urls) > 0:
                    st.subheader("Results")
                    df = pd.DataFrame(passed_urls)
                    st.dataframe(df)
                    # Download CSV
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="internal_links.csv">Download CSV File</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.info("No URLs found that meet the criteria.")

    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.text("")
    st.sidebar.markdown("Built with ❤️ by [Break The Web](https://breaktheweb.agency/)")

if __name__ == "__main__":
    main()
