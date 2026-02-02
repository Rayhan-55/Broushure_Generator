import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

def fetch_website_contents(url):
    """
    Fetch title + visible text from a webpage
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Failed to fetch {url}: {e}"

    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.title.string.strip() if soup.title else "No title found"

    if soup.body:
        for tag in soup.body(["script", "style", "img", "input", "noscript"]):
            tag.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    return (title + "\n\n" + text)[:2000]


def fetch_website_links(url):
    """
    Fetch and normalize all valid links from a webpage
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    raw_links = [a.get("href") for a in soup.find_all("a", href=True)]

    full_links = []
    for link in raw_links:
        if link.startswith("#") or link.startswith("mailto:"):
            continue
        full_links.append(urljoin(url, link))

    return list(set(full_links))  # remove duplicates
