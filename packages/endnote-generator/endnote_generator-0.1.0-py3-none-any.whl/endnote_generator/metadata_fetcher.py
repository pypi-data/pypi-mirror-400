import requests
import time
from typing import Dict, Optional

class MetadataFetcher:
    """
    Fetches bibliographic metadata for a given DOI using the Crossref API.
    """
    
    BASE_URL = "https://api.crossref.org/works/"

    def __init__(self, email: str = "agent@example.com"):
        # Crossref encourages providing an email in the User-Agent to be in the "polite pool"
        self.headers = {
            "User-Agent": f"EndNoteGenerator/1.0 (mailto:{email})"
        }

    def fetch_metadata(self, doi: str) -> Optional[Dict]:
        """
        Fetches metadata for a DOI.
        Returns a dictionary with keys expected by EndNote (Title, Author, Year, Journal, etc.)
        or None if request fails.
        """
        url = f"{self.BASE_URL}{doi}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                item = data.get('message', {})
                return self._parse_crossref_response(item)
            else:
                print(f"Failed to fetch metadata for DOI {doi}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching metadata for DOI {doi}: {e}")
            return None

    def _parse_crossref_response(self, item: Dict) -> Dict:
        """
        Parses the raw Crossref JSON into a simplified dictionary.
        """
        metadata = {
            'title': item.get('title', [''])[0],
            'journal': item.get('container-title', [''])[0],
            'doi': item.get('DOI', ''),
            'year': '',
            'volume': item.get('volume', ''),
            'issue': item.get('issue', ''),
            'pages': item.get('page', ''),
            'authors': []
        }

        # Extract Year
        issued = item.get('issued', {}).get('date-parts', [])
        if issued and len(issued[0]) > 0:
            metadata['year'] = str(issued[0][0])

        # Extract Authors
        for author in item.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                metadata['authors'].append(f"{family}, {given}")

        return metadata
