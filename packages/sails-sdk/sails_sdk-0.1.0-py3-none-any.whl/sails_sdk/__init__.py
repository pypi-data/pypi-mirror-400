import requests
from typing import Optional, Dict, Any, List

class SailsClient:
    def __init__(self, api_key: str, base_url: str = "https://sails.live/api/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        token = self.api_key.strip()
        if token.lower().startswith("bearer "):
            token = token.split(None, 1)[1]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, json=payload, headers=headers)
        if not resp.ok:
            try:
                error_data = resp.json()
                error_message = error_data.get("error", {})
                if isinstance(error_message, dict):
                    error_message = error_message.get("message", resp.text)
                raise Exception(f"Sails API Error {resp.status_code}: {error_message}")
            except ValueError:
                raise Exception(f"Sails API Error {resp.status_code}: {resp.text}")
        return resp.json()

    def predict(
                self,
                image_url: str,
                country: Optional[str] = None,
                limit: Optional[int] = None,
                description: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a price prediction request to the Sails API.
        
        Args:
            image_url (str): The URL of the image to analyze.
            country (str, optional): ISO 3166-1 alpha-2 country code. If omitted, API defaults apply.
            limit (int, optional): Max number of results to return. Omit for no limit.
            description (str, optional): Optional text description to refine the query hint.
        """
        payload = {
            "image_url": image_url
        }
        if country:
            payload["country"] = country
        if limit is not None:
            payload["limit"] = limit
        if description:
            payload["description"] = description

        return self._post("/predict-price", payload)

    def generate_basic_listing(
        self,
        image_urls: List[str],
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"image_urls": image_urls}
        if additional_info:
            payload["additional_info"] = additional_info
        return self._post("/generate-basic-listing", payload)

    def update_listing(
        self,
        brand: str,
        image_urls: List[str],
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"brand": brand, "image_urls": image_urls}
        if additional_info:
            payload["additional_info"] = additional_info
        return self._post("/update-listing", payload)

    def generate_scaffold_listing(
        self,
        scaffold: str,
        image_urls: Optional[List[str]] = None,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"scaffold": scaffold}
        if image_urls is not None:
            payload["image_urls"] = image_urls
        if additional_info:
            payload["additional_info"] = additional_info
        return self._post("/generate-scaffold-listing", payload)
