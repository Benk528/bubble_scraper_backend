from pydantic import BaseModel
from typing import List, Optional

class Link(BaseModel):
    href: str
    text: Optional[str]

class Image(BaseModel):
    src: str
    alt: Optional[str]

class Metadata(BaseModel):
    description: Optional[str]
    keywords: Optional[str]
    author: Optional[str]

class ScrapedData(BaseModel):
    page_title: str
    metadata: Metadata
    headings: List[str]
    paragraphs: List[str]
    links: List[Link]
    images: List[Image]