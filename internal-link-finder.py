import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin, urlunparse
import re

def reset_fields():
    st.session_state.uploaded_file = None
    st.session_state.site_urls = []
    st.session_state.keywords = []
    st.session_state.selector = ""
    st.session_state.target_url = ""

def normalize_url(url, base_url=None):
    """Normalize URL for comparison"""
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    parsed = urlparse(url)
    # Remove fragment and normalize
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip('/') or '/',
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))
    return normalized

def find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector):
    # Normalize target URL for comparison
    normalized_target = normalize_url(target_url)
    
    def get_content_and_links(url, selector):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content based on selector
            if selector.strip():
                try:
                    # Convert XPath to CSS selector or use BeautifulSoup directly
                    if selector.startswith('//'):
                        # For XPath, we'll use a more robust approach
                        from lxml import etree, html
                        dom = html.fromstring(response.content)
                        content_elements = dom.xpath(selector)
                        if content_elements:
                            # Get text content
                            content_text = ' '.join([elem.text_content() for elem in content_elements])
                            # Get all links within the selected area
                            all_links = []
                            for elem in content_elements:
                                links = elem.xpath('.//a/@href')
                                all_links.extend(links)
                        else:
                            content_text = soup.get_text()
                            all_links = [a.get('href') for a in soup.find_all('a', href=True)]
                    else:
                        # Assume it's a CSS selector
                        selected = soup.select(selector)
                        if selected:
                            content_text = ' '.join([elem.get_text() for elem in selected])
                            all_links = []
                            for elem in selected:
                                links = elem.find_all('a', href=True)
                                all_links.extend([link.get('href') for link in links])
                        else:
                            content_text = soup.get_text()
                            all_links = [a.get('href') for a in soup.find_all('a', href=True)]
                except Exception as selector_error:
                    st.warning(f"Selector error for {url}: {selector_error}. Using full page content.")
                    content_text = soup.get_text()
                    all_links = [a.get('href') for a in soup.find_all('a', href=True)]
            else:
                # Use full page content
                content_text = soup.get_text()
                all_links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            return url, content_text, all_links
            
        except requests.exceptions.RequestException as e:
            st.error(f"Request error for {url}: {e}")
            return url, '', []
        except Exception as e:
            st.error(f"Error processing {url}: {e}")
            return url, '', []

    def process_url(url):
        url, content, links = get_content_and_links(url, selector)
        if not content:
            return []
        
        # Check if page already links to target URL
        page_links_to_target = False
        for link in links:
            if link:
                normalized_link = normalize_url(link, url)
                if normalized_link == normalized_target:
                    page_links_to_target = True
                    break
        
        # If page already links to target, skip it
        if page_links_to_target:
            return []
        
        # Check for keywords in content
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword.strip() and keyword.lower() in content_lower:
                found_keywords.append(keyword.strip())
        
        # Return result if keywords found and no existing link to target
        if found_keywords:
            return [{
                'URL': url,
                'Keywords Found': found_keywords
            }]
        
        return []

    results = []
    processed_count = 0
    
    # Filter out empty keywords
    keywords = [k.strip() for k in keywords if k.strip()]
    
    if not keywords:
        st.error("No valid keywords provided.")
        return []
    
    with ThreadPoolExecutor(max_workers=5) as executor:  # Reduced workers to be more respectful
        futures = {executor.submit(process_url, url): url for url in site_urls}
        
        for future in as_completed(futures):
            try:
                url_results = future.result()
                if url_results:
                    results.extend(url_results)
                processed_count += 1
                
                # Show progress
                if processed_count % 10 == 0:
                    st.info(f"Processed {processed_count}/{len(site_urls)} URLs...")
                    
            except Exception as e:
                st.error(f"Error processing URL: {e}")
    
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
                # Show first few URLs for verification
                with st.expander("Preview first 5 URLs"):
                    for i, url in enumerate(site_urls[:5]):
                        st.write(f"{i+1}. {url}")
        except pd.errors.EmptyDataError:
            st.error("Uploaded file is empty. Please upload a CSV with URLs in the first column.")
        except Exception as e:
            st.error(f"Could not read the uploaded file: {e}")

    # Keywords
    st.subheader("Keywords")
    keywords_input = st.text_area("Paste relevant keywords or terms below, one per line", 
                                  placeholder="payday loans\nonline casino\ncbd vape pen", height=150)
    keywords = [k.strip() for k in keywords_input.split("\n") if k.strip()]
    
    if keywords:
        st.info(f"Keywords to search for: {', '.join(keywords)}")

    # Selector
    st.subheader("XPath/CSS Selector")
    selector = st.text_input("Optional: Enter an XPath or CSS selector to narrow down the crawl scope & avoid sitewide elements", 
                           placeholder="//div[@class='content'] or .main-content")

    # Target URL
    st.subheader("Target URL")
    target_url = st.text_input("Target URL you're looking to add internal links to", 
                              placeholder="https://breaktheweb.agency/seo/seo-timeline")
    
    if target_url:
        st.info(f"Target URL: {target_url}")

    # Run crawler
    if site_urls and keywords and target_url:
        if st.button("Run Crawler"):
            with st.spinner("Crawling in progress... be patient"):
                passed_urls = find_urls_with_keywords_and_target(site_urls, keywords, target_url, selector)
            
            st.success(f"Finished crawling {len(site_urls)} URLs. Found {len(passed_urls)} internal linking opportunities.")
            
            if passed_urls:
                df = pd.DataFrame(passed_urls)
                
                # Expand the 'Keywords Found' column into separate columns
                max_keywords = max(len(row['Keywords Found']) for row in passed_urls)
                keyword_columns = {}
                
                for i in range(max_keywords):
                    keyword_columns[f'Keyword_{i+1}'] = [
                        row['Keywords Found'][i] if i < len(row['Keywords Found']) else ''
                        for row in passed_urls
                    ]
                
                # Create final dataframe
                result_df = pd.DataFrame({
                    'URL': [row['URL'] for row in passed_urls],
                    **keyword_columns
                })
                
                st.write(result_df)
                
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV", 
                    data=csv, 
                    file_name='internal_link_suggestions.csv', 
                    mime='text/csv'
                )
            else:
                st.warning("No URLs passed all checks. This could mean:")
                st.write("- All URLs already link to the target URL")
                st.write("- None of the URLs contain the specified keywords")
                st.write("- The XPath/selector is too restrictive")
                st.write("- There were errors accessing the URLs")
            st.balloons()

    # Reset button to clear the inputs
    if st.button("Reset"):
        reset_fields()
        st.rerun()

    st.markdown("""**Run Crawler button is activated once all required fields are completed*""")

    # Add guide (keeping your original guide content)
    st.markdown("---")
    st.markdown("""
    # How to Use the Internal Link Finder Tool

    The Internal Linking Finder was built by [Break The Web](https://breaktheweb.agency) to identify URLs on a given website that do not currently link to a specified target URL and also include specific terms.

    Here's a step-by-step guide on how to use this tool:

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
