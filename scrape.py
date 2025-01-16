from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import requests
import time
from dotenv import load_dotenv
import os
import random

load_dotenv()

search = "mens winter outfits"
scroll_num_of_times = 50
path = os.getenv("WEBSCRAPE_SAVE_PATH")

if not path:
    raise ValueError("env variable doesnt exist...")

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://in.pinterest.com/ideas/")

    page.locator("[data-test-id=\"search-box-input\"]").fill(search)
    page.locator("[data-test-id=\"search-box-input\"]").press("Enter")

    time.sleep(2)

    for _ in range(1, scroll_num_of_times):
        page.mouse.wheel(0, 4000)
        time.sleep(random.uniform(1.5, 2))

    html = page.inner_html('div.vbI.XiG')

    soup = BeautifulSoup(html, 'lxml')

    for links in soup.find_all('img'):
        imageName = links.get('src').strip('https://i.pinimg.com/236x/d3/4c/fc/.jpg')
        name = imageName.replace('/', '_')+'.jpg'
        imageLink = links.get('src')
        
        with open(os.path.join(path, name), "wb") as f:
            image = requests.get(imageLink)
            f.write(image.content)

            time.sleep(0.25)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)