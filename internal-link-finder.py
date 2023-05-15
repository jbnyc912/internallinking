import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64

def find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath):
    passed_urls = []
    
    for url in site_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        keyword_found = False
        link_to_target_found = False
        
        if xpath:
            content_elements = soup.select(xpath)
            if content_elements:
                for content_element in content_elements:
                    content_text = content_element.get_text()
                    for keyword in keywords:
                        if keyword.lower() in content_text.lower():
                            keyword_found = True
                            break
                    if not keyword_found:
                        for link in content_element.find_all('a'):
                            if link.has_attr('href') and target_url in link['href']:
                                link_to_target_found = True
                                break
                        if not link_to_target_found:
                            keywords_on_page = []
                            for keyword in keywords:
                                if keyword.lower() in content_text.lower():
                                    keywords_on_page.append(keyword)
                            keywords_on_page_str = ', '.join(keywords_on_page)
                            passed_urls.append({'URL': url, 'Keywords Found': keywords_on_page_str})
                            break
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
        
    return passed_urls

def main():
    st.set_page_config(page_title="Internal Linking Finder - a Break The Web tool", page_icon=":link:")
    st.image("https://cdn-icons-png.flaticon.com/128/3093/3093852.png", width=40)
    st.title("Internal Linking Finder")
    st.markdown('*Created by [Break The Web](https://breaktheweb.agency)*')
    st.markdown("This tool allows you to identify URLs not currently linking to the Target URL and include the keyword(s).")

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
        st.markdown("*Enter the target URL you want the site URLs to link to*", unsafe_allow_html=True)
        target_url = st.text_input("", placeholder="https://example.com")

        # XPath
        st.subheader("XPath (Optional)")
        st.markdown("*Enter the XPath to narrow down the search within the HTML of each site URL*", unsafe_allow_html=True)
        xpath = st.text_input("", placeholder="//*[@id='main']")

        # Start analysis
        if st.button("Start Analysis"):
            passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, xpath)
            st.success(f"Analysis completed! Found {len(passed_urls)} opportunities.")

            # Export results
            if len(passed_urls) > 0:
                df = pd.DataFrame(passed_urls)
                csv = df.to_csv(index=False).encode()
                b64 = base64.b64encode(csv).decode()
                href = f"<a href='data:file/csv;base64,{b64}' download='internal_linking_opportunities.csv'>Download CSV</a>"
                st.markdown(f"Download the CSV file containing the opportunities: {href}", unsafe_allow_html=True)
            else:
                st.info("No opportunities found.")

if __name__ == "__main__":
    main()

