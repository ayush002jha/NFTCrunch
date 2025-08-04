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

    # --- Define each API call as a separate function ---

    def get_wallet_score(self, wallet_address: str):
        """Retrieves the risk score for a specific wallet."""
        print(f"Fetching wallet score for {wallet_address}...")
        return self._make_request("/wallet/score", params={"wallet_address": wallet_address})

    def get_wallet_label(self, wallet_address: str, blockchain: str = "ethereum"):
        """Retrieves labels associated with a wallet."""
        print(f"Fetching wallet labels for {wallet_address}...")
        return self._make_request("/wallet/label", params={"address": wallet_address, "blockchain": blockchain})

    def get_wallet_washtrade(self, wallet_address: str, blockchain: str = "ethereum"):
        """Retrieves wash trading metrics for a wallet."""
        print(f"Fetching wash trade data for {wallet_address}...")
        params = {"wallet": wallet_address, "blockchain": blockchain, "sort_by": "washtrade_volume"}
        return self._make_request("/nft/wallet/washtrade", params=params)

    def get_nft_balance(self, wallet_address: str, blockchain: str = "ethereum"):
        """Retrieves NFT holdings for a wallet."""
        print(f"Fetching NFT balance for {wallet_address}...")
        params = {"wallet": wallet_address, "blockchain": blockchain, "limit": 5} # Limit to 5 for a quick overview
        return self._make_request("/wallet/balance/nft", params=params)

    def get_token_balance(self, wallet_address: str, blockchain: str = "ethereum"):
        """Retrieves ERC-20 token holdings for a wallet."""
        print(f"Fetching token balance for {wallet_address}...")
        params = {"address": wallet_address, "blockchain": blockchain, "limit": 5} # Limit to 5 for a quick overview
        return self._make_request("/wallet/balance/token", params=params)


async def get_all_wallet_data(api_key: str, wallet_address: str):
    """
    Asynchronously fetches all required data points from the bitsCrunch API.
    """
    api = BitsCrunchAPI(api_key)
    
    # Using asyncio.to_thread to run synchronous requests concurrently
    tasks = {
        "score": asyncio.to_thread(api.get_wallet_score, wallet_address),
        "labels": asyncio.to_thread(api.get_wallet_label, wallet_address),
        "washtrade": asyncio.to_thread(api.get_wallet_washtrade, wallet_address),
        "nfts": asyncio.to_thread(api.get_nft_balance, wallet_address),
        "tokens": asyncio.to_thread(api.get_token_balance, wallet_address),
    }

    results = await asyncio.gather(*tasks.values())
    
    # Combine the keys and results into a dictionary
    return dict(zip(tasks.keys(), results))