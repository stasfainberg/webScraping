import asyncio
import aiohttp
import random
import time
from aiohttp import ClientSession
from bs4 import BeautifulSoup

class AsyncWebScraper:
    def __init__(self, urls, concurrency=5, retries=3, timeout=10):
        self.urls = urls
        self.concurrency = concurrency
        self.retries = retries
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch(self, session: ClientSession, url: str, attempt=1):
        """Fetches a URL with retry logic."""
        try:
            async with self.semaphore:  # Limit concurrent requests
                async with session.get(url, timeout=self.timeout) as response:
                    html = await response.text()
                    return html
        except Exception as e:
            if attempt < self.retries:
                print(f"Retrying {url} (Attempt {attempt + 1}) due to {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                return await self.fetch(session, url, attempt + 1)
            else:
                print(f"Failed to fetch {url} after {self.retries} attempts.")
                return None

    async def scrape(self, session: ClientSession, url: str):
        """Fetches the page and extracts data."""
        html = await self.fetch(session, url)
        if html:
            return self.parse_html(url, html)
        return None

    def parse_html(self, url, html):
        """Parses HTML and extracts data (example: page title)."""
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        print(f"Scraped {url}: {title}")
        return {"url": url, "title": title}

    async def run(self):
        """Runs the scraper asynchronously."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.scrape(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks)
            return [res for res in results if res]

if __name__ == "__main__":
    urls = [
        "https://www.python.org"
        #"https://www.github.com",
        #"https://www.openai.com",
        #"https://realpython.com",
        #"https://www.wikipedia.org"
    ]

    start_time = time.time()
    scraper = AsyncWebScraper(urls, concurrency=3)
    results = asyncio.run(scraper.run())

    print("\nFinal Results:")
    for res in results:
        print(res)

    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")

