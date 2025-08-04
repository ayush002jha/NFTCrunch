# bitscrunch_api.py (Updated for Sequential Calls)

import requests
import asyncio

class BitsCrunchAPI:
    """
    A corrected wrapper class for the UnleashNFTs (bitsCrunch) V2 API.
    """
    BASE_URL = "https://api.unleashnfts.com/api/v2"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.headers = {
            "x-api-key": api_key,
            "accept": "application/json"
        }

    def _make_request(self, endpoint: str, params: dict = None):
        """Helper function to make a GET request to the API."""
        try:
            # Using a longer timeout for individual requests
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self.headers, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {response.url}: {http_err} - {response.text}")
            return {"error": str(http_err), "details": response.text}
        except Exception as err:
            print(f"Other error occurred: {err}")
            return {"error": str(err)}

    # The individual API call functions remain the same (they are synchronous)
    def get_wallet_scores(self, wallet_address: str):
        print(f"Fetching wallet scores for {wallet_address}...")
        endpoint = "/nft/wallet/scores"
        params = {"wallet": [wallet_address], "blockchain": "ethereum", "sort_by": "portfolio_value"}
        return self._make_request(endpoint, params=params)

    def get_wallet_profile(self, wallet_address: str):
        print(f"Fetching wallet profile for {wallet_address}...")
        endpoint = "/nft/wallet/profile"
        params = {"wallet": [wallet_address]}
        return self._make_request(endpoint, params=params)

    def get_wallet_washtrade(self, wallet_address: str):
        print(f"Fetching wash trade data for {wallet_address}...")
        endpoint = "/nft/wallet/washtrade"
        params = {"wallet": [wallet_address], "blockchain": "ethereum", "sort_by": "washtrade_volume"}
        return self._make_request(endpoint, params=params)

    def get_nft_balance(self, wallet_address: str):
        print(f"Fetching NFT balance for {wallet_address}...")
        endpoint = "/wallet/balance/nft"
        params = {"wallet": [wallet_address], "blockchain": "ethereum", "limit": 5}
        return self._make_request(endpoint, params=params)

    def get_token_balance(self, wallet_address: str):
        print(f"Fetching token balance for {wallet_address}...")
        endpoint = "/wallet/balance/token"
        params = {"address": wallet_address, "blockchain": "ethereum", "limit": 5}
        return self._make_request(endpoint, params=params)

async def get_all_wallet_data(api_key: str, wallet_address: str):
    """
    Asynchronously fetches all data points SEQUENTIALLY to respect API rate limits.
    """
    api = BitsCrunchAPI(api_key)
    wallet_data = {}
    
    # We now call each function one by one with a delay.
    wallet_data['scores'] = await asyncio.to_thread(api.get_wallet_scores, wallet_address)
    await asyncio.sleep(0.5)  # Wait for 0.5 seconds before the next call

    wallet_data['profile'] = await asyncio.to_thread(api.get_wallet_profile, wallet_address)
    await asyncio.sleep(0.5)

    wallet_data['washtrade'] = await asyncio.to_thread(api.get_wallet_washtrade, wallet_address)
    await asyncio.sleep(0.5)

    wallet_data['nfts'] = await asyncio.to_thread(api.get_nft_balance, wallet_address)
    await asyncio.sleep(0.5)
    
    wallet_data['tokens'] = await asyncio.to_thread(api.get_token_balance, wallet_address)

    return wallet_data