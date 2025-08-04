# bitscrunch_api.py

import requests
import asyncio

class BitsCrunchAPI:
    """
    A wrapper class for the bitsCrunch API to fetch wallet data.
    """
    BASE_URL = "https://api.bitscrunch.com/apiV2"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, params: dict = None):
        """Helper function to make a GET request to the API."""
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self.headers, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
            return {"error": str(http_err), "details": response.text}
        except Exception as err:
            print(f"Other error occurred: {err}")
            return {"error": str(err)}