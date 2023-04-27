import requests
from bs4 import BeautifulSoup
import streamlit as st


def find_urls_with_keywords_and_target(site_urls, keywords, target_url):
    st.write("Checking URLs...")
    passed_urls = []
    for url in site_urls:
        st.write(f"Checking URL: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        keyword_found = False
        for keyword in keywords:
            if keyword.lower() in soup.get_text().lower():
                keyword_found = True
                break
        if not keyword_found:
            st.write(f"None of the keywords found in {url}")
            continue
        for link in soup.find_all("a"):
            href = link.get("href")
            if href is not None and (target_url in href or href.startswith(target_url)):
                st.write(f"{url} has a link to {target_url}")
                break
        else:
            st.write(f"{url} does not have a link to {target_url}")
            passed_urls.append(url)
    if passed_urls:
        st.write("URLs that passed all checks:")
        for passed_url in passed_urls:
            st.write(passed_url)
    else:
        st.write("No URLs passed all checks.")


def main():
    st.title("Web Crawler App")
    site_urls = st.text_area("Site URLs", "https://www.google.com\nhttps://www.github.com")
    site_urls = site_urls.split("\n")
    keywords = st.text_area("Keywords", "Python\nStreamlit\nWeb scraping")
    keywords = keywords.split("\n")
    target_url = st.text_input("Target URL")
    if st.button("Run Crawler"):
        find_urls_with_keywords_and_target(site_urls, keywords, target_url)


if __name__ == "__main__":
    main()
    
    if passed_urls:
        st.write("URLs that passed all checks:")
        for passed_url in passed_urls:
            st.write(passed_url)
        
        # Export results to CSV
        data = {"URL": passed_urls, "Keyword": [", ".join(keywords)] * len(passed_urls)}
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="results.csv">Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.write("No URLs passed all checks.")

