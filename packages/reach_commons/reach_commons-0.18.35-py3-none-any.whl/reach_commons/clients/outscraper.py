import os

import requests


class OutscraperClient:
    TOKENS = {
        "Staging": "MjZjYWUyMzg4MzUxNDk2Zjk0OGRlOTFlMzkyMDhhYWF8M2Q5ZGU2NDI0YQ",
        "Prod": "MjZjYWUyMzg4MzUxNDk2Zjk0OGRlOTFlMzkyMDhhYWF8M2Q5ZGU2NDI0YQ",
    }

    WEBHOOKS = {
        "Staging": "https://api-staging.getreach.ai/webhooks/data-bridge/outscraper/scraper-completed?token=tRm4k75N9hK1vF0dSwIi0HcMyV",
        "Prod": "https://api.getreach.ai/webhooks/data-bridge/outscraper/scraper-completed?token=tRm4k75N9hK1vF0dSwIi0HcMyV",
    }

    def __init__(self, token=None, webhook_url=None):
        self.environment = os.environ.get("ENV", "Staging")
        self.base_url = "https://api.app.outscraper.com"
        self.token = token or self.TOKENS.get(self.environment)
        self.webhook_url = webhook_url or self.WEBHOOKS.get(self.environment)

    @property
    def headers(self):
        common_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        return {**common_headers, "X-API-KEY": self.token}

    def search_google_maps_reviews(
        self, google_place_id: str, start_from: int = None, cutoff=None
    ):
        params = {
            "query": google_place_id,
            "webhook": self.webhook_url,
            "reviewsLimit": 0,
        }
        if start_from:
            params["start"] = start_from
        if cutoff:
            params["cutoff"] = cutoff
        resp = requests.get(
            f"{self.base_url}/maps/reviews-v3",
            headers=self.headers,
            params=params,
        )
        return resp

    def get_job_details(self, job_id: str):
        """Perform a GET request to retrieve details for a specific job using its job_id."""
        url = f"{self.base_url}/requests/{job_id}"
        response = requests.get(url, headers=self.headers)
        return response

    def get_balance(self):
        url = f"{self.base_url}/profile/balance"
        response = requests.get(url, headers=self.headers)
        return response
