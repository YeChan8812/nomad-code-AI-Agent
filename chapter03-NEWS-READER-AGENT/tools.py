from crewai.tools import tool
from crewai_tools import SerperDevTool
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# playwright를 사용하기 위해서는 먼저 uv add playwright로 모듈 설치!
# 그 다음 uv run playwright install로 사용할 수 있는 chromium을 설치해 줘야 됨!

@tool
def count_letters(sentence: str):
    """ 
    This function is to count the amount of letters in a sentence.
    The input is a 'sentence' string.
    The output is a number. 
    """
    return len(sentence)

search_tool = SerperDevTool(n_results=30)

@tool
def scrape_tool(url: str):
    """
    Use this when you need to read the content of a website.
    Returns the content of a website, in case the website is not available, it returns 'No content'.
    Input should be a 'url' string. for example ("https://www.csis.org/blogs/latest-southeast-asia/latest-southeast-asia-2nd-cambodia-thailand-ceasefire")
    """

    print(f"Scrapping URL: {url}")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)
        html = page.content()

        browser.close()

        soup = BeautifulSoup(html, "html.parser")

        unwanted_tags = ["header", "footer", "nav", "aside", "script", "style", "noscript", "iframe", "form", "button", "input", "select", "textarea", "img", "svg", "canvas", "audio", "video", "embed", "object"]

        for tag in soup.find_all(unwanted_tags):
            tag.decompose()

        content = soup.get_text(separator=" ")

        return content if content != "" else "No content"