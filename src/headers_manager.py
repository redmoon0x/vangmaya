import random
from typing import Dict, List, Optional

class HeadersManager:
    def __init__(self):
        # Common origins for request spoofing
        self.origins = [
            'https://ai4bharat.iitm.ac.in',
            'https://ai4bharat.org',
            'https://www.ai4bharat.org',
            'https://models.ai4bharat.org',
            'https://indicnlp.ai4bharat.org'
        ]

        # Common accept-language values with weights
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.8',
            'hi-IN,hi;q=0.9,en;q=0.8',
            'mr-IN,mr;q=0.9,en;q=0.8',
            'ta-IN,ta;q=0.9,en;q=0.8',
            'te-IN,te;q=0.9,en;q=0.8',
            'kn-IN,kn;q=0.9,en;q=0.8',
            'ml-IN,ml;q=0.9,en;q=0.8',
            'gu-IN,gu;q=0.9,en;q=0.8',
            'bn-IN,bn;q=0.9,en;q=0.8',
            'pa-IN,pa;q=0.9,en;q=0.8',
            'or-IN,or;q=0.9,en;q=0.8'
        ]

        self._current_headers: Optional[Dict[str, str]] = None

    def get_random_origin(self) -> str:
        """Get a random origin."""
        return random.choice(self.origins)

    def get_random_accept_language(self) -> str:
        """Get a random accept-language header."""
        return random.choice(self.accept_languages)

    def get_random_headers(self, base_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get random headers including origin and accept-language.
        Optionally merge with base headers.
        """
        headers = base_headers.copy() if base_headers else {}
        
        # Add or update random headers
        origin = self.get_random_origin()
        headers.update({
            'authority': 'admin.models.ai4bharat.org',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': self.get_random_accept_language(),
            'content-type': 'application/json',
            'origin': origin,
            'priority': 'u=1, i',
            'referer': f"{origin}/",
            'sec-ch-ua': '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1'
        })

        self._current_headers = headers
        return headers

    def get_current_headers(self) -> Optional[Dict[str, str]]:
        """Get the currently selected headers."""
        return self._current_headers.copy() if self._current_headers else None

    def add_origin(self, origin: str) -> None:
        """Add a custom origin to the list."""
        if origin not in self.origins:
            self.origins.append(origin)

    def add_accept_language(self, accept_language: str) -> None:
        """Add a custom accept-language to the list."""
        if accept_language not in self.accept_languages:
            self.accept_languages.append(accept_language)

    def remove_origin(self, origin: str) -> bool:
        """Remove an origin from the list."""
        if origin in self.origins and len(self.origins) > 1:
            self.origins.remove(origin)
            return True
        return False

    def remove_accept_language(self, accept_language: str) -> bool:
        """Remove an accept-language from the list."""
        if accept_language in self.accept_languages and len(self.accept_languages) > 1:
            self.accept_languages.remove(accept_language)
            return True
        return False

    def get_all_origins(self) -> List[str]:
        """Get all available origins."""
        return self.origins.copy()

    def get_all_accept_languages(self) -> List[str]:
        """Get all available accept-languages."""
        return self.accept_languages.copy()
