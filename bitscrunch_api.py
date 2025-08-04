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
            response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {response.url}: {http_err} - {response.text}")
            return {"error": str(http_err), "details": response.text}
        except Exception as err:
            print(f"Other error occurred: {err}")
            return {"error": str(err)}

    # --- Define each API call with corrected endpoints and parameters ---

    def get_wallet_scores(self, wallet_address: str):
        """Retrieves score values for a specific wallet."""
        print(f"Fetching wallet scores for {wallet_address}...")
        endpoint = "/nft/wallet/scores"
        params = {
            "wallet": [wallet_address],
            "blockchain": "ethereum",
            "sort_by": "portfolio_value"
        }
        return self._make_request(endpoint, params=params)

    def get_wallet_profile(self, wallet_address: str):
        """Retrieves the profile of a wallet to find labels."""
        print(f"Fetching wallet profile for {wallet_address}...")
        endpoint = "/nft/wallet/profile"
        params = {"wallet": [wallet_address]}
        return self._make_request(endpoint, params=params)

    def get_wallet_washtrade(self, wallet_address: str):
        """Retrieves wash trading metrics for a wallet."""
        print(f"Fetching wash trade data for {wallet_address}...")
        endpoint = "/nft/wallet/washtrade"
        params = {
            "wallet": [wallet_address],
            "blockchain": "ethereum",
            "sort_by": "washtrade_volume"
        }
        return self._make_request(endpoint, params=params)

    def get_nft_balance(self, wallet_address: str):
        """Retrieves NFT holdings for a wallet."""
        print(f"Fetching NFT balance for {wallet_address}...")
        # Assuming this endpoint is still valid or has a similar structure
        endpoint = "/wallet/balance/nft"
        params = {
            "wallet": [wallet_address],
            "blockchain": "ethereum",
            "limit": 5
        }
        # This endpoint might not exist in the new docs, so we handle potential errors
        return self._make_request(endpoint, params=params)

    def get_token_balance(self, wallet_address: str):
        """Retrieves ERC-20 token holdings for a wallet."""
        print(f"Fetching token balance for {wallet_address}...")
        # Assuming this endpoint is still valid or has a similar structure
        endpoint = "/wallet/balance/token"
        params = {
            "address": wallet_address,
            "blockchain": "ethereum",
            "limit": 5
        }
        # This endpoint might not exist in the new docs, so we handle potential errors
        return self._make_request(endpoint, params=params)

async def get_all_wallet_data(api_key: str, wallet_address: str):
    """Asynchronously fetches all required data points from the API."""
    api = BitsCrunchAPI(api_key)
    
    # Run synchronous requests concurrently using asyncio.to_thread
    tasks = {
        "scores": asyncio.to_thread(api.get_wallet_scores, wallet_address),
        "profile": asyncio.to_thread(api.get_wallet_profile, wallet_address),
        "washtrade": asyncio.to_thread(api.get_wallet_washtrade, wallet_address),
        "nfts": asyncio.to_thread(api.get_nft_balance, wallet_address),
        "tokens": asyncio.to_thread(api.get_token_balance, wallet_address),
    }

    results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))