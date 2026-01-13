"""
High-level search functions for EasyLCSC4KiCAD.

Provides convenient search functions that wrap the low-level client API
and return typed data models.
"""

import logging
from typing import Literal

from easylcsc4kicad.client import APIError, EasyEDAClient
from easylcsc4kicad.models import Component, Footprint, SearchResult, Symbol

logger = logging.getLogger(__name__)


def _parse_component_from_easyeda(data: dict) -> Component:
    """Parse EasyEDA component API response into Component model."""
    result = data.get("result", {})

    # Extract datasheet from nested structure
    datasheet_url = ""
    data_str = result.get("dataStr", {})
    if isinstance(data_str, dict):
        head = data_str.get("head", {})
        c_para = head.get("c_para", {})
        datasheet_url = c_para.get("link", "")

    # Determine component type and create appropriate model
    component = Component(
        uuid=result.get("uuid", ""),
        title=result.get("title", "").replace(" ", "_").replace("/", "_"),
        lcsc_id=result.get("componentId"),
        description=result.get("description", ""),
        datasheet_url=datasheet_url,
        manufacturer=result.get("manufacturer", ""),
        category=result.get("category", ""),
        attributes=result.get("attributes", {}),
    )

    return component


def _parse_search_results(data: dict, source: str = "easyeda") -> SearchResult:
    """Parse search API response into SearchResult model."""
    results = []

    if source == "lcsc":
        # LCSC API response structure
        product_list = data.get("result", {}).get("productList", [])
        total = data.get("result", {}).get("total", 0)
        page = data.get("result", {}).get("currentPage", 1)
        page_size = data.get("result", {}).get("pageSize", 20)

        for item in product_list:
            component = Component(
                uuid=str(item.get("productId", "")),
                title=item.get("productModel", ""),
                lcsc_id=item.get("productCode", ""),
                description=item.get("productDescription", ""),
                datasheet_url=item.get("pdfUrl", ""),
                manufacturer=item.get("brandNameEn", ""),
                category=item.get("parentCatalogName", ""),
                attributes={
                    "Package": item.get("encapStandard", ""),
                    "Min Buy": str(item.get("minBuyNumber", "")),
                    "Stock": str(item.get("stockNumber", "")),
                    "Price": str(item.get("productPriceList", [])),
                },
            )
            results.append(component)

        return SearchResult(
            total=total,
            page=page,
            items_per_page=page_size,
            results=results,
        )

    else:
        # EasyEDA API response structure
        result_data = data.get("result", {})

        # Handle different response formats
        if isinstance(result_data, list):
            items = result_data
            total = len(items)
            page = 1
            page_size = len(items)
        else:
            # Check for Pro API 'lists' structure
            if "lists" in result_data:
                lists = result_data["lists"]
                # Merge LCSC and User results
                items = lists.get("lcsc", []) + lists.get("user", [])
                total = len(
                    items
                )  # Pagination is per-category in Pro API, but rough total here
                page = 1
                page_size = len(items)
            else:
                items = result_data.get("list", result_data.get("data", []))
                total = result_data.get("total", len(items))
                page = result_data.get("page", 1)
                page_size = result_data.get("pageSize", 20)

        for item in items:
            # Extract attributes if available
            attributes = item.get("attributes", {})
            datasheet_url = item.get("datasheet", attributes.get("Datasheet", ""))
            manufacturer = item.get("manufacturer", attributes.get("Manufacturer", ""))

            # Try to get LCSC ID from various places
            lcsc_id = item.get(
                "lcsc",
                item.get(
                    "componentId",
                    item.get("product_code", attributes.get("Supplier Part")),
                ),
            )

            component = Component(
                uuid=item.get("uuid", item.get("component_uuid", "")),
                title=item.get("title", item.get("name", "")),
                lcsc_id=lcsc_id,
                description=item.get("description", ""),
                datasheet_url=datasheet_url,
                manufacturer=manufacturer,
                category=item.get("category", ""),
                attributes=attributes,
            )
            results.append(component)

        return SearchResult(
            total=total,
            page=page,
            items_per_page=page_size,
            results=results,
        )


def search(
    keyword: str,
    source: Literal["all", "lcsc", "easyeda"] = "all",
    page: int = 1,
    page_size: int = 20,
    component_type: str = "device",
) -> SearchResult:
    """
    Search for components across LCSC and EasyEDA.

    Args:
        keyword: Search keyword (part number, name, or description)
        source: Search source - "all", "lcsc", or "easyeda"
        page: Page number (1-indexed)
        page_size: Results per page
        component_type: Type to search ("device", "symbol", "footprint", "3d")

    Returns:
        SearchResult with matching components
    """
    client = EasyEDAClient()
    results: list[Component] = []
    total = 0

    if source in ("all", "easyeda"):
        try:
            data = client.search_easyeda(
                keyword=keyword,
                page=page,
                page_size=page_size,
                component_type=component_type,
            )
            easyeda_results = _parse_search_results(data, "easyeda")
            results.extend(easyeda_results.results)
            total += easyeda_results.total
        except APIError as e:
            logger.warning(f"EasyEDA search failed: {e}")

    if source in ("all", "lcsc"):
        try:
            data = client.search_lcsc(
                keyword=keyword,
                page=page,
                page_size=page_size,
            )
            lcsc_results = _parse_search_results(data, "lcsc")
            results.extend(lcsc_results.results)
            total += lcsc_results.total
        except APIError as e:
            logger.warning(f"LCSC search failed: {e}")

    return SearchResult(
        total=total,
        page=page,
        items_per_page=page_size,
        results=results,
    )


def get_by_lcsc_id(lcsc_id: str) -> Component | None:
    """
    Get component details by LCSC part number.

    Args:
        lcsc_id: LCSC part number (e.g., "C1337258")

    Returns:
        Component with symbol/footprint UUIDs if found, None otherwise
    """
    client = EasyEDAClient()

    try:
        # Try searching via Pro API first as it returns complete details
        search_data = client.search_easyeda(lcsc_id)
        search_results = _parse_search_results(search_data, "easyeda")

        if search_results.total > 0:
            # Find exact match if possible, otherwise take first
            for comp in search_results.results:
                if comp.lcsc_id == lcsc_id or comp.title == lcsc_id:
                    return comp
            return search_results.results[0]

        # Fallback to standard API (get_component_svgs)
        data = client.get_component_svgs(lcsc_id)

        if not data.get("success", False):
            logger.warning(f"Component not found: {lcsc_id}")
            return None

        result = data.get("result", [])
        if not result:
            return None

        # Extract symbol and footprint UUIDs
        # Last item is typically the footprint, others are symbols
        symbols: list[Symbol] = []
        footprints: list[Footprint] = []

        for i, item in enumerate(result):
            uuid = item.get("component_uuid", "")
            title = item.get("title", f"Part_{i}")

            if i == len(result) - 1:
                # Last item is footprint
                footprints.append(
                    Footprint(
                        uuid=uuid,
                        title=title,
                    )
                )
            else:
                # Others are symbols
                symbols.append(
                    Symbol(
                        uuid=uuid,
                        title=title,
                    )
                )

        # Create component with extracted data
        component = Component(
            uuid=result[0].get("component_uuid", "") if result else "",
            title=lcsc_id,
            lcsc_id=lcsc_id,
            symbols=symbols,
            footprints=footprints,
        )

        # Try to get more details from the first component
        if component.uuid:
            try:
                detail_data = client.get_component(component.uuid)
                if detail_data.get("success", False):
                    detailed = _parse_component_from_easyeda(detail_data)
                    component.title = detailed.title or lcsc_id
                    component.description = detailed.description
                    component.datasheet_url = detailed.datasheet_url
                    component.manufacturer = detailed.manufacturer
                    component.category = detailed.category
            except APIError:
                pass  # Keep partial data

        return component

    except APIError as e:
        logger.error(f"Failed to get component {lcsc_id}: {e}")
        return None


def search_footprints(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> SearchResult:
    """
    Search specifically for footprints.

    Args:
        keyword: Search keyword
        page: Page number
        page_size: Results per page

    Returns:
        SearchResult with matching footprints
    """
    return search(
        keyword=keyword,
        source="easyeda",
        page=page,
        page_size=page_size,
        component_type="footprint",
    )


def search_symbols(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> SearchResult:
    """
    Search specifically for schematic symbols.

    Args:
        keyword: Search keyword
        page: Page number
        page_size: Results per page

    Returns:
        SearchResult with matching symbols
    """
    return search(
        keyword=keyword,
        source="easyeda",
        page=page,
        page_size=page_size,
        component_type="symbol",
    )


def search_3d_models(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> SearchResult:
    """
    Search specifically for 3D models.

    Args:
        keyword: Search keyword
        page: Page number
        page_size: Results per page

    Returns:
        SearchResult with matching 3D models
    """
    return search(
        keyword=keyword,
        source="easyeda",
        page=page,
        page_size=page_size,
        component_type="3d",
    )
