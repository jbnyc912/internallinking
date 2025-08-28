import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
from urllib.parse import urlparse, urljoin

def reset_fields():
    st.session_state.uploaded_file = None
    st.session_state.site_urls = []
    st.session_state.keywords = []
    st.session_state.selector = ""
    st.session_state.target_url = ""

def find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector):
    def get_content_area(url, selector):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if selector.strip():
                try:
                    dom = etree.HTML(str(soup))
                    content_area = dom.xpath(selector)
                    if content_area:
                        # Fix: Use proper text extraction method
                        content_text = etree.tostring(content_area[0], method='text', encoding='unicode')
                        links = [a.get('href') for a in content_area[0].xpath('.//a[@href]')]
                        return url, content_text, links
                    else:
                        # Fallback to full page if selector doesn't match
                        content_text = soup.get_text()
                        links = [a.get('href') for a in soup.find_all('a', href=True)]
                        return url, content_text, links
                except Exception:
                    # Fallback to full page if XPath fails
                    content_text = soup.get_text()
                    links = [a.get('href') for a in soup.find_all('a', href=True)]
                    return url, content_text, links
            else:
                # No selector provided, use full page
                content_text = soup.get_text()
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                return url, content_text, links
                
        except Exception as e:
            st.error(f"Error fetching content area for {url}: {e}")
            return url, '', []

    def process_url(url):
        url, content, links = get_content_area(url, selector)
        if not content:
            return []
        
        # Fix: Check if page already links to target URL first
        parsed_target_url = urlparse(target_url)
        target_normalized = target_url.rstrip('/').lower()
        target_path_normalized = parsed_target_url.path.rstrip('/').lower()
        
        already_links_to_target = False
        for link in links:
            if link:
                full_link = urljoin(url, link) if not link.startswith('http') else link
                full_link_normalized = full_link.rstrip('/').lower()
                link_normalized = link.rstrip('/').lower()
                
                if (link_normalized == target_normalized or 
                    link_normalized == target_path_normalized or
                    full_link_normalized == target_normalized):
                    already_links_to_target = True
                    break
        
        # If already links to target, skip this URL
        if already_links_to_target:
            return []
        
        # Now check for keywords (case-insensitive)
        local_results = []
        found_anchors = []
        content_lower = content.lower()
        for keyword in keywords:
            if keyword.strip() and keyword.strip().lower() in content_lower:
                found_anchors.append(keyword.strip())
        
        if found_anchors:
            local_results.append({
                'URL': url,
                'Keywords Found': found_anchors
            })
        return local_results

    results = []
    # Filter out empty keywords
    keywords = [k.strip() for k in keywords if k.strip()]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_url, url): url for url in site_urls}
        for future in as_completed(futures):
            url_results = future.result()
            if url_results:
                results.extend(url_results)
    return results

def main():
    st.set_page_config(page_title="Internal Linking Finder - a Break The Web tool", page_icon=":link:")
    st.image("https://cdn-icons-png.flaticon.com/128/9841/9841627.png", width=40)
    st.title("Internal Linking Finder")
    st.markdown("""
    This tool allows you to identify URLs not currently linking to the Target URL, and also include the keyword(s).

    For more details on how to use this tool, see the [guide](#how-to-use-the-internal-link-finder-tool) below.
    """)

    # CSV upload
    st.subheader("Source URLs")
    site_urls = []
    uploaded_file = st.file_uploader(
        "First, upload the list of URLs you would like to check in a CSV file with the URLs in column A and no header",
        type="csv"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python')
            site_urls = df.iloc[:, 0].dropna().astype(str).tolist()
    
            if not site_urls:
                st.error("No valid URLs found in the first column of your CSV.")
            else:
                st.success(f"Found {len(site_urls)} URLs.")
        except pd.errors.EmptyDataError:
            st.error("Uploaded file is empty. Please upload a CSV with URLs in the first column.")
        except Exception as e:
            st.error(f"Could not read the uploaded file: {e}")

    # Keywords
    st.subheader("Keywords")
    keywords = st.text_area("Paste relevant keywords or terms below, one per line", placeholder="payday loans\nonline casino\ncbd vape pen", height=150)
    keywords = keywords.split("\n")

    # Selector
    st.subheader("XPath")
    selector = st.text_input("Optional: Enter an XPath to narrow down the crawl scope & avoid sitewide elements", placeholder="Enter XPath selector (e.g., //div[@class='content'])")

    # Target URL
    st.subheader("Target URL")
    target_url = st.text_input("Target URL you're looking to add internal links to", placeholder="https://breaktheweb.agency/seo/seo-timeline")

    # Run crawler
    if site_urls and keywords and target_url:
        if st.button("Run Crawler"):
            with st.spinner("Crawling in progress... be patient"):
                passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector)
            st.success(f"Finished crawling {len(site_urls)} URLs. Found {len(passed_urls)} internal linking opportunities.")
            
            if passed_urls:
                df = pd.DataFrame(passed_urls)
                # Expand the 'Keywords Found' column into separate columns
                keyword_df = df['Keywords Found'].apply(pd.Series)
                keyword_df.columns = [f'Keyword_{i+1}' for i in range(len(keyword_df.columns))]
                df = pd.concat([df['URL'], keyword_df], axis=1)
                st.write(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Download CSV", data=csv, file_name='internal_link_suggestions.csv', mime='text/csv')
            else:
                st.warning("No URLs passed all checks.")
            st.balloons()

    # Reset button to clear the inputs
    if st.button("Reset"):
        reset_fields()
        st.rerun()

    st.markdown("""**Run Crawler button is activated once all required fields are completed*""")

    # Add guide
    st.markdown("---")
    st.markdown("""
    # How to Use the Internal Link Finder Tool

    The Internal Linking Finder was built by [Break The Web](https://breaktheweb.agency) to identify URLs on a given website that do not currently link to a specified target URL and also include specific terms.

    Here's a step-by-Step guide on how to use this tool:

    ## Step 1: Upload Source URLs

    The first step in using the tool is to upload a list of URLs that you want to check. These URLs should be in a CSV file, with the URLs listed in column A and no header. This list can be gathered from a Sitemap or crawler such as Screaming Frog or Sitebulb.

    The more fine-tuned the list is, the faster the tool will work and the better the results.

    ## Step 2: Enter Keywords

    Next, enter the relevant keywords or terms that you want to check for in the URLs. These should be pasted into the text area under the "Keywords" section, one keyword per line.

    Keep in mind that some keywords might not be grammatically correct or natural in context, so be sure to use words that would be realistic anchors if deemed suitable.

    ## Step 3: Specify an XPath (Optional)

    If you want to narrow down the crawl scope and avoid sitewide links in the main header or footer, you can enter an XPath from the source URL. This is optional, but highly recommended.

    Locate the section of the page in a source URL that contains the page content (blog article, page body template, etc.) and right-clicking that section > Select Inspect > In dev tools, drag your mouse up the hierarchy to locate the parent code that covers that section, ensuring header/footer are not highlighted > Right-click the code > Copy > Copy XPath.

    ## Step 4: Enter the Target URL

    Enter the URL that you're looking to add internal links to in the "Target URL" section.

    ## Step 5: Run the Crawler

    Once you've entered all the necessary information, click the "Run Crawler" button to start the crawling process. The tool will then crawl each Source URL, checking for the presence of the specified keywords and whether each URL links to the target URL.

    ## Step 6: View and Download Results

    After the crawl is complete, the tool will display the number of URLs that passed all checks. If any URLs passed, you can download the results as a CSV file by clicking the "Download CSV" button.

    ## Step 7: Reset (Optional)

    If you want to run a new crawl with different parameters, click the "Reset" button to clear all fields and start over.
    """)

if __name__ == "__main__":
    main()
