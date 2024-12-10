from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright

# Import the ScrapedData schema from schema.py
from schema import ScrapedData

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape", response_model=ScrapedData)
async def scrape_data(scrape_request: ScrapeRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Open the target URL
            await page.goto(scrape_request.url)

            # Extract data
            page_title = await page.title()
            metadata = await page.evaluate(
                """() => {
                    return {
                        description: document.querySelector('meta[name="description"]')?.content || null,
                        keywords: document.querySelector('meta[name="keywords"]')?.content || null,
                        author: document.querySelector('meta[name="author"]')?.content || null
                    };
                }"""
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

            # Validate and return the structured JSON
            data = ScrapedData(
                page_title=page_title,
                metadata=metadata,
                headings=headings,
                paragraphs=paragraphs,
                links=links,
                images=images,
            )
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))