"""
Web Scraper Module
Extracts main content from blog URLs using trafilatura
"""

import trafilatura
from trafilatura.settings import use_config
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from rich.console import Console

console = Console()


@dataclass
class BlogContent:
    """Structured blog content"""
    title: str
    text: str
    author: Optional[str] = None
    date: Optional[str] = None
    url: str = ""


class BlogScraper:
    """Scrapes and extracts content from blog URLs"""
    
    def __init__(self):
        # Configure trafilatura for better extraction
        self.config = use_config()
        self.config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
        
    def scrape(self, url: str) -> BlogContent:
        """
        Scrape blog content from URL
        
        Args:
            url: The blog URL to scrape
            
        Returns:
            BlogContent object with extracted data
        """
        console.print(f"[blue]🌐 Fetching content from:[/blue] {url}")
        
        try:
            # Try trafilatura first (best for article extraction)
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                # Extract main content
                text = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=False,
                    no_fallback=False,
                    config=self.config
                )
                
                # Get metadata
                metadata = trafilatura.extract_metadata(downloaded)
                
                if text:
                    console.print("[green]✓ Content extracted successfully[/green]")
                    return BlogContent(
                        title=metadata.title if metadata and metadata.title else self._extract_title_fallback(url),
                        text=text,
                        author=metadata.author if metadata else None,
                        date=metadata.date if metadata else None,
                        url=url
                    )
            
            # Fallback to BeautifulSoup
            console.print("[yellow]⚠ Primary extraction failed, trying fallback...[/yellow]")
            return self._fallback_scrape(url)
            
        except Exception as e:
            console.print(f"[red]✗ Error scraping URL: {e}[/red]")
            raise
    
    def _fallback_scrape(self, url: str) -> BlogContent:
        """Fallback scraping using BeautifulSoup"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ads']):
            element.decompose()
        
        # Try to find the main content
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        
        if article:
            text = article.get_text(separator='\n', strip=True)
        else:
            # Get body text as last resort
            text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
        
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        title = soup.title.string if soup.title else "Untitled"
        
        console.print("[green]✓ Content extracted via fallback[/green]")
        
        return BlogContent(
            title=title,
            text=text,
            url=url
        )
    
    def _extract_title_fallback(self, url: str) -> str:
        """Extract title from URL as fallback"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.title.string if soup.title else "Untitled Blog Post"
        except:
            return "Untitled Blog Post"


def scrape_blog(url: str) -> BlogContent:
    """Convenience function to scrape a blog URL"""
    scraper = BlogScraper()
    return scraper.scrape(url)


if __name__ == "__main__":
    # Test the scraper
    test_url = input("Enter a blog URL to test: ")
    content = scrape_blog(test_url)
    print(f"\nTitle: {content.title}")
    print(f"Author: {content.author}")
    print(f"Date: {content.date}")
    print(f"\nContent Preview:\n{content.text[:500]}...")
