import os
from typing import List, Optional

from demo_data import SAMPLE_REPORT
from apify_client import run_actor, get_actor_run_results
from datetime import datetime


def fetch_rental_listings(address: str) -> List[dict]:
    """Call the Apify rental-listing Actor."""
    return []


def fetch_google_reviews(company: str) -> List[dict]:
    """Call the Apify Google Reviews Actor."""
    return []


def fetch_facebook_posts(query: str) -> List[dict]:
    """Call the Apify Facebook Actor."""
    actor_name = "scrapeforge/facebook-search-posts"
    actor_input = {
        "query": query,
        "maxPosts": 50,
    }
    try:
        run_data = run_actor(actor_name, actor_input, timeout_seconds=180)
    except Exception:
        return []

    run_id = run_data.get("id")
    if not run_id:
        return []

    try:
        items = get_actor_run_results(run_id)
    except Exception:
        return []

    normalized = []
    for it in items:
        # Apify facebook scraper returns keys like `post_id`, `url`, `message`, `timestamp`, `author`
        timestamp = it.get("timestamp") or it.get("createdAt") or it.get("date")
        date_str = None
        try:
            if isinstance(timestamp, (int, float)):
                date_str = datetime.fromtimestamp(int(timestamp)).isoformat()
            elif isinstance(timestamp, str) and timestamp.isdigit():
                date_str = datetime.fromtimestamp(int(timestamp)).isoformat()
            else:
                date_str = timestamp
        except Exception:
            date_str = None

        text = it.get("message") or it.get("message_rich") or it.get("text") or ""
        author = (it.get("author") or {}).get("name") if isinstance(it.get("author"), dict) else None

        normalized.append({
            "title": author or it.get("post_id") or it.get("id") or "Facebook post",
            "date": date_str,
            "url": it.get("url"),
            "text": text,
            "raw": it,
        })

    return normalized


def fetch_reddit_posts(query: str) -> List[dict]:
    """Call the Apify Reddit Actor."""
    return []


def index_in_elasticsearch(documents: List[dict]) -> None:
    """Store normalized documents in Elasticsearch."""
    pass


def search_elasticsearch(query: str) -> List[dict]:
    """Search property, company, complaint, and rental data."""
    return []


def generate_summary(report: dict) -> str:
    """Generate an LLM summary using only retrieved evidence."""
    return "This is a placeholder summary. Replace with an LLM-generated report when the service is connected."


def fetch_property_data(address: str, management_company: Optional[str] = None, property_name: Optional[str] = None) -> dict:
    """Placeholder for rental property lookup and aggregation."""
    facebook_results = []
    try:
        facebook_results = fetch_facebook_posts(address)
    except Exception:
        facebook_results = []

    return {
        "address": address,
        "property_name": property_name or "Unknown Property",
        "management_company": management_company or "Unknown Management",
        "current_rent": 0,
        "nearby_median_rent": 0,
        "rent_diff_pct": 0.0,
        "data_confidence": "Low",
        "company_matches": [],
        "complaints": [],
        "landlord_history": [],
        "nearby_rentals": [],
        "evidence": [],
        "facebook_posts": facebook_results,
        "summary": "Replace this stub with actual property, complaint, and evidence data once the external services are connected.",
    }
