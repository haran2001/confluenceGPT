# confluence_scraper/scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class ConfluenceScraper:
    def __init__(self, base_url, depth=1, headers=None, visited=None, filter_external=True):
        """
        :param base_url: The Confluence page URL to start scraping from
        :param depth: Max depth to recursively follow links
        :param headers: HTTP headers (for authentication, content-type, etc.)
        :param visited: A set to keep track of visited URLs
        :param filter_external: Boolean to indicate if external (non-Confluence) URLs should be ignored
        """
        self.base_url = base_url
        self.depth = depth
        self.headers = headers or {}
        self.visited = visited if visited is not None else set()
        self.filter_external = filter_external

    def scrape_page(self, url, current_depth=0):
        """
        Recursively scrape a Confluence page and return structured data.
        """
        if url in self.visited:
            return None
        if current_depth > self.depth:
            return None

        self.visited.add(url)

        # GET request to fetch page HTML
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text
        page_text = self._extract_text(soup)
        # Extract tables
        tables = self._extract_tables(soup)
        # Extract images
        images = self._extract_images(soup, url)

        data = {
            "url": url,
            "text": page_text,
            "tables": tables,
            "images": images,
            "subpages": []
        }

        # Recursive follow links
        if current_depth < self.depth:
            links = self._extract_links(soup, url)
            for link in links:
                child_data = self.scrape_page(link, current_depth + 1)
                if child_data:
                    data["subpages"].append(child_data)

        return data

    def _extract_links(self, soup, current_url):
        """
        Extract and filter links from the page. 
        Filter out external links if filter_external=True
        """
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(current_url, href)

            if self.filter_external:
                # Ensure it's within the same domain (basic check) or starts with the base Confluence domain.
                if self.base_url in full_url:
                    links.add(full_url)
            else:
                links.add(full_url)

        return list(links)

    def _extract_text(self, soup):
        """
        Extract all relevant textual content from the HTML
        """
        # Optionally remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator="\n").strip()

    def _extract_tables(self, soup):
        """
        Extract tables into a structured list of lists (like CSV) or dict
        """
        tables_data = []
        tables = soup.find_all('table')
        for table in tables:
            table_rows = table.find_all('tr')
            table_data = []
            for row in table_rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [col.get_text(strip=True) for col in cols]
                table_data.append(cols_text)
            tables_data.append(table_data)
        return tables_data

    def _extract_images(self, soup, page_url):
        """
        Extract image URLs (optionally convert to base64)
        """
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags:
            img_url = urljoin(page_url, img['src'])
            alt_text = img.get('alt', '')
            images.append({
                'url': img_url,
                'alt': alt_text
            })
        return images


# Example usage of the scraper
# if __name__ == "__main__":
#     BASE_URL = "https://your-confluence-domain.com/somepage"
#     scraper = ConfluenceScraper(BASE_URL, depth=1)
#     result = scraper.scrape_page(BASE_URL)
#     print(result)  # This will print the nested JSON-like structure
