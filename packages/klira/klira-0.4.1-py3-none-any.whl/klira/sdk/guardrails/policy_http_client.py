"""HTTP client for fetching policies from remote API."""

import time
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


class PolicyHTTPClient:
    """HTTP client for fetching policies from Klira API."""

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.getklira.com/v1/policies",
        timeout: int = 10,
        retries: int = 3,
    ):
        """
        Initialize HTTP client.

        Args:
            api_key: Klira API key (must start with 'klira_')
            api_url: Full API URL (default: https://api.getklira.com/v1/policies)
            timeout: Request timeout in seconds
            retries: Number of retry attempts on failure
        """
        if not api_key or not api_key.startswith("klira_"):
            raise ValueError("Invalid API key - must start with 'klira_'")

        self.api_url = api_url
        self.timeout = timeout
        self.retries = retries
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def fetch_policies(self) -> Dict[str, Any]:
        """
        Fetch policies from API endpoint.

        This is called ONCE during SDK initialization.

        Returns:
            Dict with keys: version, updated_at, policies

        Raises:
            requests.RequestException: On HTTP errors
            ValueError: On invalid response format
        """
        for attempt in range(self.retries):
            try:
                logger.info(
                    f"Fetching policies from {self.api_url} (attempt {attempt + 1}/{self.retries})"
                )

                response = requests.get(
                    self.api_url, headers=self.headers, timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                # Validate response format
                self._validate_response(data)

                logger.info(
                    f"Successfully fetched policies "
                    f"(version: {data.get('version')}, count: {len(data.get('policies', []))})"
                )

                return data

            except requests.RequestException as e:
                logger.warning(f"Policy fetch attempt {attempt + 1} failed: {e}")

                if attempt < self.retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    sleep_time = 2**attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    # Final attempt failed
                    logger.error(
                        f"Failed to fetch policies after {self.retries} attempts"
                    )
                    raise

        # This line is unreachable but added for mypy
        raise RuntimeError(
            "Failed to fetch policies after all retries"
        )  # pragma: no cover

    def _validate_response(self, data: Dict[str, Any]) -> None:
        """
        Validate API response format.

        Expected format:
        {
            "version": "1.0.0",
            "updated_at": "2025-11-04T12:00:00Z",
            "policies": [...]
        }
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict response, got {type(data)}")

        if "policies" not in data:
            raise ValueError("Response missing 'policies' field")

        if not isinstance(data["policies"], list):
            raise ValueError(
                f"Expected 'policies' to be list, got {type(data['policies'])}"
            )

        # Optional fields
        if "version" not in data:
            logger.warning("Response missing 'version' field")

        if "updated_at" not in data:
            logger.warning("Response missing 'updated_at' field")
