from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from database import save_scrape, init_db, get_all_scrapes, get_scrapes_by_user
import os
import pdfplumber
import base64
from typing import Optional
from supabase import create_client  # ✅ NEW

# ✅ No need to re-import pydantic and Optional again here

# Debugging Environment Variables
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

    # Define a root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Scraper API"}

@app.get("/scrapes/{user_id}", summary="Get all scrapes for a specific user")
def get_scrapes_for_user(user_id: str):
    scrapes = get_scrapes_by_user(user_id)
    return {"scrapes": scrapes}

class ScrapeRequest(BaseModel):
    url: str
    user_id: str
    client_chatbot_id: Optional[str] = None
    business_name: Optional[str] = None
    logo_url: Optional[str] = None

class PDFScrapeRequest(BaseModel):
    """
    Request body for scraping PDF files.
    """
    pdf_base64: str
    user_id: str
    filename: Optional[str] = "uploaded.pdf"

@app.post("/scrape-website", summary="Scrape a website and extract structured data")
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

            if scrape_request.client_chatbot_id:
                chatbot_data = {
                    "bubble_client_chatbot_id": scrape_request.client_chatbot_id,
                    "business_name": scrape_request.business_name,
                    "logo_url": scrape_request.logo_url,
                    "scraped_text": "\n".join(paragraphs),
                }

                supabase.table("client_chatbots").upsert(
                    chatbot_data,
                    on_conflict="bubble_client_chatbot_id"
                ).execute()

                return {
                    "message": "Scrape successful (client_chatbot)",
                    "chatbot_id": scrape_request.client_chatbot_id,
                    "data": chatbot_data
                }
            else:
                scraped_data = {
                    "user_id": scrape_request.user_id,
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

@app.get("/scrapes", summary="Get all scrapes for all users")
def get_scrapes():
    scrapes = get_all_scrapes()
    return {"scrapes": scrapes}

@app.post("/scrape-pdf", summary="Extract text from a PDF file (base64-encoded)")
async def scrape_pdf(scrape_request: PDFScrapeRequest):
    print("Received PDF scrape request:")
    try:
        print(f"user_id: {scrape_request.user_id}")
        print(f"filename: {scrape_request.filename}")
        print(f"pdf_base64 (first 50 chars): {scrape_request.pdf_base64[:50]}")

        # Sanitize the filename
        safe_filename = os.path.basename(scrape_request.filename)

        # Decode and save the PDF
        pdf_bytes = base64.b64decode(scrape_request.pdf_base64)
        with open(safe_filename, "wb") as f:
            f.write(pdf_bytes)  # <-- This line was mis-indented in your version

        # Extract text from PDF
        content = []
        with pdfplumber.open(safe_filename) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content.append(text)

        full_text = "\n".join(content)

        scraped_data = {
            "user_id": scrape_request.user_id,
            "page_title": safe_filename,
            "meta_data": {},
            "headings": [],
            "paragraphs": [full_text],
            "links": [],
            "images": []
        }

        scrape_id = save_scrape(scraped_data)

        return {
            "message": "PDF Scrape successful",
            "scrape_id": scrape_id,
            "data": scraped_data
        }

    except Exception as e:
        print("❌ Error during PDF scrape:", e)
        raise HTTPException(status_code=500, detail=str(e))