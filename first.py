import streamlit as st
import json
from scraper import fetch_website_contents, fetch_website_links
from openai import OpenAI

# ========== CONFIG ==========
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "llama3.2:1b"

ollama = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"
)

# ========== SYSTEM PROMPTS ==========
link_system_prompt = """
You are provided with a list of links found on a webpage.
Decide which links are useful for a company brochure (About, Careers, Company, etc).

Respond strictly in JSON:

{
  "links": [
    {"type": "about page", "url": "https://example.com/about"}
  ]
}
"""

brochure_system_prompt = """
You analyze company website content and generate a short brochure.
Respond in markdown.
Include company mission, culture, customers and careers if available.
"""

# ========== HELPERS ==========
def get_links_user_prompt(url):
    links = fetch_website_links(url)
    return f"""
Here are links from {url}.
Choose only relevant company links.
Ignore privacy, terms, email links.

Links:
{chr(10).join(links)}
"""

def select_relevant_links(url):
    response = ollama.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def fetch_page_and_links(url):
    content = fetch_website_contents(url)
    relevant = select_relevant_links(url)

    text = f"## Landing Page\n{content}\n"
    for link in relevant["links"]:
        text += f"\n## {link['type']}\n"
        text += fetch_website_contents(link["url"])

    return text[:5000]  # safety limit

def stream_brochure(company, url):
    prompt = f"""
Company Name: {company}

Website Content:
{fetch_page_and_links(url)}
"""

    stream = ollama.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    output = ""
    placeholder = st.empty()

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            output += delta
            placeholder.markdown(output)

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="AI Brochure Generator", layout="centered")

st.title("📄 AI Website Brochure Generator")
st.caption("Powered by Ollama + LLaMA + Streamlit")

company = st.text_input("Company / Organization Name")
url = st.text_input("Website URL")

if st.button("Generate Brochure 🚀"):
    if not company or not url:
        st.warning("Please enter both company name and URL")
    else:
        with st.spinner("Analyzing website & generating brochure..."):
            stream_brochure(company, url)
