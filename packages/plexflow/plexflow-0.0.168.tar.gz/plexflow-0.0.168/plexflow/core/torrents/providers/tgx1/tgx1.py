import logging
import time
from urllib.parse import quote, urlparse, parse_qs
from typing import List, Optional

from plexflow.utils.api.rest.plexful import Plexful
from plexflow.core.torrents.providers.tgx1.utils import TGX1SearchResult

logger = logging.getLogger(__name__)

MAX_RECURSION_GUARD = 20  # Safety cap to prevent infinite pagination
THROTTLE_DELAY = 1.2      # Seconds between API calls

class TGX1(Plexful):
    """TorrentGalaxy API provider with dynamic pagination support."""
    DEFAULT_BASE_URL = 'https://torrentgalaxy.one'

    def __init__(self, base_url: str = DEFAULT_BASE_URL, **kwargs):
        super().__init__(base_url=base_url, **kwargs)

    def _build_url(self, term: str, page: int) -> str:
        safe_term = quote(term)
        url = f'/get-posts/keywords:{safe_term}:format:json'
        return f"{url}?page={page}" if page > 1 else url

    def search(self, imdb_id: Optional[str] = None, query: Optional[str] = None, 
               headless: bool = True, **kwargs) -> List[TGX1SearchResult]:
        
        all_results = []
        search_term = imdb_id or query
        if not search_term:
            return []

        current_page = 1
        while current_page <= MAX_RECURSION_GUARD:
            url = self._build_url(search_term, current_page)
            logging.info(f"TGX1 Requesting: Page {current_page} | {url}")
            
            try:
                response = self.get(url=url, headless=headless, **kwargs)
                data = response.json() if headless else (response.json if not callable(response.json) else response.json())
                
                if not data or not isinstance(data, dict):
                    break

                results = data.get("results", [])
                all_results.extend([TGX1SearchResult(**r) for r in results if isinstance(r, dict)])

                # LOGIC: Check if another page exists in the API links
                next_page_url = data.get("links", {}).get("next")
                if not next_page_url:
                    logging.info(f"TGX1: Reached the last page ({current_page}).")
                    break
                
                current_page += 1
                time.sleep(THROTTLE_DELAY)
            except Exception as e:
                logging.error(f"TGX1 failure on page {current_page}: {e}")
                break
        
        return all_results

if __name__ == '__main__':
    # Usage Example
    logging.basicConfig(level=logging.INFO)
    tgx = TGX1()
    
    # Search via IMDB ID
    results = tgx.search(imdb_id='tt4574334')
    
    # Search via Query (demonstrating URL encoding)
    # results = tgx.search(query='Spider-Man: Across the Spider-Verse')

    print(f"Total results found: {len(results)}")
    for torrent in results:  # Print first 3 for brevity
        print(f"[{torrent.release_name}] -> {torrent.magnet[:50]}...")