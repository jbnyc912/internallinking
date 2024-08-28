
import streamlit as st
import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin

# Reset fields function (carried over from the old file)
def reset_fields():
    uploaded_file = None
    site_urls = []
    keywords = []
    selector = ""
    target_url = ""

# The main function which ties everything together
def main():
    st.title("Internal Link Finder Tool")

    # Placeholder for instructions visibility state
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = False

    # Function to show or hide instructions
    def toggle_instructions():
        st.session_state.show_instructions = not st.session_state.show_instructions

    # Input fields with example placeholders in a two-column layout
    col1, col2 = st.columns([2, 2])

    with col1:
        urls_input = st.text_area("Source URLs (one per line)", placeholder="https://example.com/page1\nhttps://example.com/page2")
        xpath_input = st.text_input("XPath Selector (Optional)", placeholder="//div[@class='content']")
        anchor_texts_input = st.text_area("Anchor Texts (one per line)", placeholder="keyword1\nkeyword2")
        target_url_input = st.text_input("Target URL", placeholder="https://example.com/target")

    with col2:
        # Function to get the content area using XPath and all <a> links
        def get_content_area(url, xpath):
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                dom = etree.HTML(str(soup))
                content_area = dom.xpath(xpath)
                if content_area:
                    content_text = ''.join(content_area[0].itertext())
                    links = [a.get('href') for a in content_area[0].xpath('.//a')]
                    return url, content_text, links
                else:
                    return url, '', []
            except Exception as e:
                st.error(f"Error fetching content area for {url}: {e}")
                return url, '', []

        # Function to process each URL
        def process_url(url):
            url, content, links = get_content_area(url, xpath_input)
            return url, content, links

    if st.button("Run Crawler"):
        if not urls_input or not anchor_texts_input or not target_url_input:
            st.error("Please fill in all required fields.")
        else:
            urls = urls_input.strip().split("\n")
            anchor_texts = anchor_texts_input.strip().split("\n")
            target_url = target_url_input.strip()

            passed_urls = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(process_url, url): url for url in urls}
                for future in as_completed(futures):
                    url, content, links = future.result()
                    if any(anchor_text.lower() in content.lower() for anchor_text in anchor_texts) and not any(target_url in link for link in links):
                        passed_urls.append(url)

            if passed_urls:
                st.success(f"Found {len(passed_urls)} URLs that match the criteria.")
                df = pd.DataFrame({"Passed URLs": passed_urls})
                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV", data=csv, file_name='internal_link_suggestions.csv', mime='text/csv')
            else:
                st.info("No URLs found with the specified criteria.")

    # Reset button to clear the inputs
    if st.button("Reset"):
        reset_fields()
        st.experimental_rerun()

    # Add the "How to Use" button at the bottom, toggle visibility of instructions
    st.button("How to Use", on_click=toggle_instructions)

    if st.session_state.show_instructions:
        st.markdown("""
        ## How to Use the Internal Link Finder Tool

        The Internal Linking Finder was built by Break The Web to identify URLs on a given website that do not currently link to a specified target URL and also include specific terms.

        ### Step 1: Enter Source URLs
        Upload a list of URLs that you want to check. One per line. This list can be gathered from a Sitemap or crawler such as Screaming Frog or Sitebulb.

        ### Step 2: Enter Keywords
        Enter the relevant keywords or terms that you want to check for in the URLs. These should be pasted into the text area under the "Keywords" section, one keyword per line.

        ### Step 3: Specify an HTML Selector (Optional)
        If you want to narrow down the crawl scope and avoid sitewide links in the main header or footer, you can enter an HTML selector from the source URL. This is optional, but highly recommended.

        ### Step 4: Enter the Target URL
        Enter the URL that you're looking to add internal links to in the "Target URL" section.

        ### Step 5: Run the Crawler
        Click the "Run Crawler" button to start the crawling process. The tool will then crawl each Source URL, checking for the presence of the specified keywords and whether each URL links to the target URL.

        ### Step 6: View and Download Results
        After the crawl is complete, the tool will display the number of URLs that passed all checks. If any URLs passed, you can download the results as a CSV file by clicking the "Download CSV" button.

        ### Step 7: Reset (Optional)
        Click the "Reset" button to clear all fields and start over.
        """)
        
if __name__ == "__main__":
    main()
