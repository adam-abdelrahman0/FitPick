from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import requests
import time
from dotenv import load_dotenv
import os
import random
import json

load_dotenv()

search = "mens winter outfits"
max_scrolls = 100
path = os.getenv("WEBSCRAPE_SAVE_PATH")

if not path:
    raise ValueError("env variable doesnt exist...")

def run(playwright: Playwright) -> None:
   # browser = playwright.chromium.launch(executable_path=os.getenv("CHROME_PATH"), headless=False)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://in.pinterest.com/ideas/")

    page.locator("[data-test-id=\"search-box-input\"]").fill(search)
    page.locator("[data-test-id=\"search-box-input\"]").press("Enter")

    time.sleep(2)

    images = []
    last_height = 0
    scrolls_completed = 0

    for scroll in range(max_scrolls):
        # Scroll down
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)  # Allow new content to load

        # Extract image URLs
        new_images = page.evaluate("""
            Array.from(document.querySelectorAll('img')).map(img => img.src)
        """)

        # Add new images to the list
        images.extend(new_images)

        # Remove duplicates
        images = list(set(images))

        # Check if page height has stopped increasing
        current_height = page.evaluate("document.body.scrollHeight")
        scrolls_completed+=1
        if current_height == last_height:
            break
        last_height = current_height

    # Save to a JSON file
    with open(f"{search}_images.json", "w") as f:
        json.dump(images, f)

    # ---------------------
    context.close()
    browser.close()

    print(len(images))

    for image in images:
        image_name = image.strip('https://i.pinimg.com/236x/d3/4c/fc/.jpg')
        image_name = image_name.replace('/', '_')+'.jpg'

        with open(os.path.join(path, image_name), "wb") as f:
            image = requests.get(image)
            f.write(image.content)

            time.sleep(0.25)


with sync_playwright() as playwright:
    run(playwright)