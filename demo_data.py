SAMPLE_REPORT = {
    "address": "123 Main St, Anytown, USA",
    "property_name": "Oakwood Apartments",
    "management_company": "ABC Properties",
    "current_rent": 2100,
    "nearby_median_rent": 2350,
    "rent_diff_pct": 10.6,
    "data_confidence": "Medium",
    "company_matches": [
        {
            "company_name": "ABC Property Management LLC",
            "confidence": "High",
            "matched_sources": ["Zillow", "Apartments.com"],
        }
    ],
    "complaints": [
        {
            "category": "Maintenance Delay",
            "severity": "High",
            "source": "Google Reviews",
            "date": "2026-07-18",
            "excerpt": "Maintenance requests are often ignored for weeks, leaving units in disrepair.",
            "link": "https://example.com/google-review-1",
            "verified": False,
        },
        {
            "category": "Lease Term Violation",
            "severity": "Verified",
            "source": "City Housing Records",
            "date": "2026-05-09",
            "excerpt": "A verified violation was issued after the landlord failed to provide required notice for a rent increase.",
            "link": "https://example.com/city-record",
            "verified": True,
        },
        {
            "category": "Poor Communication",
            "severity": "Medium",
            "source": "Reddit",
            "date": "2026-06-04",
            "excerpt": "Several tenants report unanswered messages and unclear move-out instructions.",
            "link": "https://reddit.com/example-post",
            "verified": False,
        },
    ],
    "landlord_history": [
        {
            "property": "Maple Grove Towers",
            "city": "Anytown",
            "issues": 3,
            "complaint_count": 18,
            "last_reported": "2026-06-20",
        },
        {
            "property": "Riverside Lofts",
            "city": "Anytown",
            "issues": 2,
            "complaint_count": 12,
            "last_reported": "2026-05-30",
        },
    ],
    "nearby_rentals": [
        {"name": "Sunset View", "rent": 2380},
        {"name": "Elm Court", "rent": 2490},
        {"name": "Cedar Flats", "rent": 2275},
        {"name": "Oakwood Apartments", "rent": 2100},
    ],
    "evidence": [
        {
            "title": "Zillow listing details",
            "source": "Zillow",
            "note": "Management company name and local listing information.",
        },
        {
            "title": "Google Reviews thread",
            "source": "Google Reviews",
            "note": "Tenant complaints about maintenance and communication.",
        },
        {
            "title": "Local rental violation",
            "source": "Housing Authority",
            "note": "Verified notice related to lease terms.",
        },
    ],
    "summary": "This property has a moderate risk level. Several reports mention delayed maintenance and inconsistent communication, and a verified lease violation was recorded for the management company.",
}
