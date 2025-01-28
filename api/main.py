from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from database import save_scrape, init_db, get_all_scrapes
import os

# Debugging Environment Variables
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

    # Define a root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Scraper API"}

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
async def scrape_data(scrape_request: ScrapeRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(scrape_request.url)

            # Extract data
            page_title = await page.title()
            meta_data = await page.evaluate(
                """() => ({
                    description: document.querySelector('meta[name="description"]')?.content || null,
                    keywords: document.querySelector('meta[name="keywords"]')?.content || null,
                    author: document.querySelector('meta[name="author"]')?.content || null
                })"""
            )
            headings = await page.evaluate(
                """() => Array.from(document.querySelectorAll('h1, h2, h3'), h => h.textContent.trim())"""
            )
            paragraphs = await page.evaluate(
                """() => Array.from(document.querySelectorAll('p'), p => p.textContent.trim())"""
            )
            links = await page.evaluate(
                """() => Array.from(document.querySelectorAll('a'), a => ({
                    href: a.href,
                    text: a.textContent.trim()
                }))"""
            )
            images = await page.evaluate(
                """() => Array.from(document.querySelectorAll('img'), img => ({
                    src: img.src,
                    alt: img.alt || null
                }))"""
            )

            await browser.close()

            scraped_data = {
                "page_title": page_title,
                "meta_data": meta_data,
                "headings": headings,
                "paragraphs": paragraphs,
                "links": links,
                "images": images,
            }

            scrape_id = save_scrape(scraped_data)

            return {
                "message": "Scrape successful",
                "scrape_id": scrape_id,
                "data": scraped_data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scrapes")
def get_scrapes():
    scrapes = get_all_scrapes()
    return {"scrapes": scrapes}