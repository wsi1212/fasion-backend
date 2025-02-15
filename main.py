import time
from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class SearchQuery(BaseModel):
    keyword: str
    limit: int = 10

def google_image_crawler(search_query, num_images=10):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=ko-KR")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    search_url = f"https://www.google.com/search?hl=ko&gl=kr&tbm=isch&q={search_query}"
    driver.get(search_url)

    body = driver.find_element(By.TAG_NAME, "body")

    img_urls = set()
    scroll_count = 0

    while len(img_urls) < num_images and scroll_count < 10:
        body.send_keys(Keys.END)
        time.sleep(1)

        img_elements = driver.find_elements(By.CSS_SELECTOR, "img")
        img_urls.update(img.get_attribute("src") for img in img_elements if
                        img.get_attribute("src") and img.get_attribute("src").startswith("https://encrypted-tbn0.gstatic.com/images?q=") and len(img.get_attribute("src"))==92)

        scroll_count += 1

    driver.quit()

    return list(img_urls)[:num_images]


@app.get("/crawl_images/")
async def crawl_images(keyword: str = Query(..., alias="keyword"), limit: int = Query(10, alias="limit")):
    try:
        # Call the crawler function with query parameters
        image_urls = google_image_crawler(keyword, limit)

        return JSONResponse(content={"images": image_urls}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
