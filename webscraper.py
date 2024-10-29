import requests
from bs4 import BeautifulSoup

def fetch_page_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}  # Mimic a browser user agent to avoid blocks
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch data from {url} with status code {response.status_code}")
        return None

def search_study_on_site(site_url, search_path, title):
    # Step 1: Build the search URL
    search_url = f"{site_url}{search_path}{title.replace(' ', '+')}"
    print(f"Searching {search_url}")

    # Step 2: Fetch page content
    html_content = fetch_page_content(search_url)
    if not html_content:
        return f"Could not access {site_url}."

    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 3: Check if the search result has the desired title
    try:
        # Example selector - will vary by site
        result_link = soup.find('h3')  # Adjust this selector based on site's HTML
        result_title = result_link.get_text() if result_link else None
        if title.lower() not in result_title.lower():
            return f"Title not found on {site_url}."

        # Navigate to the article page by finding the link
        article_url = result_link.find('a')['href']
        article_content = fetch_page_content(article_url)
        if not article_content:
            return f"Failed to load article page on {site_url}."

        # Parse the article page
        article_soup = BeautifulSoup(article_content, 'html.parser')

        # Step 4: Check for "Conclusion" header
        conclusion_found = bool(article_soup.find(string="Conclusion"))

        # Step 5: Check for paywall markers (e.g., specific classes that appear in paywalled content)
        paywall_present = bool(article_soup.find(class_="paywall"))  # Adjust class as needed

        # Return the results
        return {
            "title_match": title.lower() in result_title.lower(),
            "conclusion_found": conclusion_found,
            "paywall_present": paywall_present,
            "article_url": article_url
        }

    except AttributeError:
        return f"No results found on {site_url} for title '{title}'"

sites = [
    {"site_name": "Google Scholar", "url": "https://scholar.google.com", "search_path": "/scholar?q="},
    {"site_name": "PubMed", "url": "https://pubmed.ncbi.nlm.nih.gov", "search_path": "/?term="},
    {"site_name": "Anna's Archive", "url": "https://annas-archive.org", "search_path": "/search?q="},
    {"site_name": "arXiv", "url": "https://arxiv.org", "search_path": "/search/?query="},
]
title = "The Therapeutic Potential of Psilocybin"


for site in sites:
    result = search_study_on_site(site["url"], site["search_path"], title)
    print(f"Results for {site['site_name']}: {result}")

    # If a valid result with the title is found, break the loop
    if isinstance(result, dict) and result["title_match"]:
        break
