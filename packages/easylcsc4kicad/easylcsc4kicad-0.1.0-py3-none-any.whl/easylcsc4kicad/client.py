"""
HTTP client for EasyEDA and LCSC APIs.

Handles all HTTP communication with EasyEDA and LCSC servers,
including search, component retrieval, and pagination.
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class EasyEDAClient:
    """HTTP client for EasyEDA/LCSC APIs."""

    # EasyEDA Standard API
    BASE_URL = "https://easyeda.com/api"

    # EasyEDA Pro API (pro.lceda.cn / pro.easyeda.com)
    PRO_BASE_URL = "https://pro.easyeda.com/api"

    # Specific UUIDs observed in HAR
    LCSC_USER_ID = "0819f05c4eef4c71ace90d822a990e87"

    DEFAULT_TIMEOUT = 30
    DEFAULT_PAGE_SIZE = 50

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://pro.easyeda.com/editor",
                "Origin": "https://pro.easyeda.com",
            }
        )

    def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request and return JSON response."""
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise APIError(
                str(e), e.response.status_code if e.response else None
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise APIError(str(e)) from e
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
            raise APIError(f"Invalid JSON response: {e}") from e

    def _get(self, url: str, params: dict | None = None) -> dict[str, Any]:
        """Make GET request."""
        return self._request("GET", url, params=params)

    def _post(self, url: str, data: dict | None = None) -> dict[str, Any]:
        """Make POST request."""
        # Note: EasyEDA expects form-urlencoded data for search, not JSON body
        return self._request("POST", url, data=data)

    # -------------------------------------------------------------------------
    # EasyEDA Standard API methods
    # -------------------------------------------------------------------------

    def get_component_svgs(self, component_id: str) -> dict[str, Any]:
        """
        Get component SVGs and UUIDs by LCSC part number.

        Args:
            component_id: LCSC part number (e.g., "C1337258")

        Returns:
            dict with 'success' boolean and 'result' containing component UUIDs
        """
        url = f"{self.BASE_URL}/products/{component_id}/svgs"
        logger.debug(f"Fetching component SVGs: {url}")
        return self._get(url)

    def get_component(self, uuid: str) -> dict[str, Any]:
        """
        Get component details by UUID.

        Args:
            uuid: Component UUID (e.g., "0819f05c4eef4c71ace90d822a990e87")

        Returns:
            dict with component data including shape, title, etc.
        """
        url = f"{self.BASE_URL}/components/{uuid}"
        logger.debug(f"Fetching component: {url}")
        return self._get(url)

    def search_easyeda(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        component_type: str = "device",
    ) -> dict[str, Any]:
        """
        Search EasyEDA component library using Pro API.

        Args:
            keyword: Search keyword
            page: Page number (1-indexed)
            page_size: Results per page
            component_type: Type of component (mapped internally)

        Returns:
            dict with search results
        """
        url = f"{self.PRO_BASE_URL}/v2/devices/search"

        data = {
            "page": page,
            "pageSize": page_size,
            "uid": self.LCSC_USER_ID,
            "path": self.LCSC_USER_ID,
            "wd": keyword,
            "returnListStyle": "classifyarr",
        }

        logger.debug(f"Searching EasyEDA Pro: {url} with {data}")
        return self._post(url, data=data)

    # -------------------------------------------------------------------------
    # LCSC API methods
    # -------------------------------------------------------------------------

    def search_lcsc(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """
        Search LCSC component database.

        Note: The EasyEDA Pro search actually returns LCSC results too,
        so usually search_easyeda is sufficient. This endpoint is kept
        for direct LCSC searches if needed.
        """
        # Based on EasyEDA Pro usage, LCSC search is integrated
        return self.search_easyeda(keyword, page, page_size)

    # -------------------------------------------------------------------------
    # Pro API methods (pro.lceda.cn)
    # -------------------------------------------------------------------------

    def search_pro_devices(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        library_uuid: str | None = None,
    ) -> dict[str, Any]:
        return self.search_easyeda(keyword, page, page_size)

    def search_pro_footprints(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        library_uuid: str | None = None,
    ) -> dict[str, Any]:
        # For footprint search, we might need a different endpoint or parameter
        # But for now, device search often includes footprints
        return self.search_easyeda(keyword, page, page_size)

    def search_pro_symbols(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        library_uuid: str | None = None,
    ) -> dict[str, Any]:
        return self.search_easyeda(keyword, page, page_size)

    def search_pro_3d(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        return self.search_easyeda(keyword, page, page_size)
