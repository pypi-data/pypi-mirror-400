"""
Food Hygiene MCP Server

Exposes UK Food Hygiene Rating Scheme (FHRS) data via MCP tools.
Data covers England, Wales, and Northern Ireland.

Structure:
    1. Configuration (API base, headers)
    2. Business type mappings
    3. API client helper
    4. MCP tools (search_establishments, get_establishment_details)
    5. Entry point
"""

import httpx
from mcp.server.fastmcp import FastMCP

# =============================================================================
# Configuration
# =============================================================================

API_BASE = "https://api.ratings.food.gov.uk"
API_HEADERS = {"x-api-version": "2"}

# =============================================================================
# Business Type Mappings
# =============================================================================

# Maps common names to FSA business type IDs
BUSINESS_TYPES = {
    "restaurant": 1,
    "cafe": 1,
    "canteen": 1,
    "takeaway": 7844,
    "sandwich shop": 7844,
    "pub": 7843,
    "bar": 7843,
    "nightclub": 7843,
    "hotel": 7842,
    "b&b": 7842,
    "guest house": 7842,
    "supermarket": 7840,
    "hypermarket": 7840,
    "school": 7845,
    "college": 7845,
    "university": 7845,
    "mobile caterer": 7846,
    "food truck": 7846,
    "hospital": 5,
    "care home": 5,
    "childcare": 5,
}

mcp = FastMCP("Food Hygiene UK")

# =============================================================================
# API Client
# =============================================================================


async def fetch_fsa(endpoint: str, params: dict | None = None) -> dict:
    """Make an async request to the FSA API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{API_BASE}{endpoint}",
            headers=API_HEADERS,
            params=params,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool()
async def search_establishments(
    name: str | None = None,
    address: str | None = None,
    postcode: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_miles: float = 1.0,
    business_type: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """
    Search for food establishments by name, location, or rating.

    Args:
        name: Business name (partial match)
        address: Street or area
        postcode: UK postcode
        latitude: Latitude for geo-search (requires longitude)
        longitude: Longitude for geo-search (requires latitude)
        radius_miles: Max distance in miles for geo-search (default 1)
        business_type: Type like "restaurant", "takeaway", "pub", "cafe", "hotel", "supermarket"
        min_rating: Minimum hygiene rating (0-5)
        max_rating: Maximum hygiene rating (0-5)
        page: Page number (default 1)
        page_size: Results per page (default 10, max 100)

    Returns:
        List of matching establishments with name, address, rating, and inspection date
    """
    params = {
        "pageNumber": page,
        "pageSize": min(page_size, 100),
    }

    if name:
        params["name"] = name
    if address:
        params["address"] = address
    if postcode:
        params["address"] = postcode  # API uses address field for postcode too

    # Geo-search
    if latitude is not None and longitude is not None:
        params["latitude"] = latitude
        params["longitude"] = longitude
        params["maxDistanceLimit"] = radius_miles * 1609.34  # Convert to meters

    # Business type
    if business_type:
        type_key = business_type.lower().strip()
        if type_key in BUSINESS_TYPES:
            params["businessTypeId"] = BUSINESS_TYPES[type_key]
        else:
            return {
                "error": f"Unknown business type: {business_type}",
                "valid_types": list(set(BUSINESS_TYPES.keys())),
            }

    # Rating filter - use API operators when possible
    rating_key = None
    rating_operator = None

    if min_rating is not None and max_rating is None:
        rating_key = min_rating
        rating_operator = "GreaterThanOrEqual"
    elif max_rating is not None and min_rating is None:
        rating_key = max_rating
        rating_operator = "LessThanOrEqual"
    elif min_rating is not None and max_rating is not None:
        # API doesn't support range - we'll use min and filter client-side
        rating_key = min_rating
        rating_operator = "GreaterThanOrEqual"

    if rating_key is not None:
        params["ratingKey"] = rating_key
        params["ratingOperatorKey"] = rating_operator

    data = await fetch_fsa("/Establishments", params)

    establishments = data.get("establishments", [])

    # Client-side filter for max_rating when we have a range
    if min_rating is not None and max_rating is not None:
        establishments = [
            e for e in establishments
            if e.get("RatingValue", "").isdigit()
            and int(e["RatingValue"]) <= max_rating
        ]

    results = []
    for e in establishments:
        results.append({
            "fhrs_id": e.get("FHRSID"),
            "name": e.get("BusinessName"),
            "address": ", ".join(filter(None, [
                e.get("AddressLine1"),
                e.get("AddressLine2"),
                e.get("AddressLine3"),
                e.get("AddressLine4"),
                e.get("PostCode"),
            ])),
            "rating": e.get("RatingValue"),
            "rating_date": e.get("RatingDate"),
            "business_type": e.get("BusinessType"),
        })

    return {
        "total": data.get("meta", {}).get("totalCount", len(results)),
        "page": page,
        "page_size": page_size,
        "establishments": results,
    }


@mcp.tool()
async def get_establishment_details(fhrs_id: int) -> dict:
    """
    Get full details for a specific establishment by its FHRS ID.

    Args:
        fhrs_id: The establishment ID (from search results)

    Returns:
        Full details including rating breakdown, inspection date, and local authority
    """
    data = await fetch_fsa(f"/Establishments/{fhrs_id}")

    # Extract scores if available
    scores = {}
    if data.get("scores"):
        scores = {
            "hygiene": data["scores"].get("Hygiene"),
            "structural": data["scores"].get("Structural"),
            "confidence_in_management": data["scores"].get("ConfidenceInManagement"),
        }

    return {
        "fhrs_id": data.get("FHRSID"),
        "name": data.get("BusinessName"),
        "business_type": data.get("BusinessType"),
        "address": ", ".join(filter(None, [
            data.get("AddressLine1"),
            data.get("AddressLine2"),
            data.get("AddressLine3"),
            data.get("AddressLine4"),
            data.get("PostCode"),
        ])),
        "postcode": data.get("PostCode"),
        "rating": data.get("RatingValue"),
        "rating_date": data.get("RatingDate"),
        "scores": scores if scores else None,
        "local_authority": {
            "name": data.get("LocalAuthorityName"),
            "email": data.get("LocalAuthorityEmailAddress"),
            "website": data.get("LocalAuthorityWebSite"),
        },
        "geocode": {
            "latitude": data.get("geocode", {}).get("latitude"),
            "longitude": data.get("geocode", {}).get("longitude"),
        } if data.get("geocode") else None,
        "right_to_reply": data.get("RightToReply") or None,
    }


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
