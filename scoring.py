import re


def normalize_address(address: str) -> str:
    replacements = {
        "Street": "St",
        "street": "St",
        "Road": "Rd",
        "road": "Rd",
        "Avenue": "Ave",
        "avenue": "Ave",
        "Apartment": "Apt",
        "apartment": "Apt",
        "Unit": "#",
        "unit": "#",
    }
    normalized = address
    for key, value in replacements.items():
        normalized = normalized.replace(key, value)
    return normalized.strip()


def normalize_company_name(name: str) -> str:
    cleaned = re.sub(r"\b(LLC|Inc|Corp|Co|Company|Limited|L\.L\.C\.|INC|CORP)\b", "", name, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^A-Za-z0-9 ]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().lower()


def compare_company_names(a: str, b: str) -> bool:
    return normalize_company_name(a) == normalize_company_name(b)


def calculate_risk_score(report: dict) -> dict:
    """Compute a Rental Trust Score from the report data."""
    score = 100
    reasons = []

    for complaint in report.get("complaints", []):
        severity = complaint.get("severity", "Low")
        verified = complaint.get("verified", False)
        if verified:
            score -= 15
            reasons.append("Verified violation")
        if severity == "High":
            score -= 10
            reasons.append("High-severity complaint")
        elif severity == "Medium":
            score -= 5
            reasons.append("Medium-severity complaint")
        elif severity == "Low":
            score -= 2
            reasons.append("Low-severity complaint")

    if report.get("landlord_history"):
        if any(record.get("issues", 0) > 1 for record in report["landlord_history"]):
            score -= 10
            reasons.append("Repeated landlord issue")

    if report.get("rent_diff_pct", 0) >= 20:
        score -= 8
        reasons.append("Rent over 20% below nearby median")

    if len(report.get("company_matches", [])) > 1:
        score -= 5
        reasons.append("Conflicting company information")

    score = max(0, min(100, score))
    if score >= 80:
        risk_level = "Low Risk"
    elif score >= 60:
        risk_level = "Moderate Risk"
    elif score >= 40:
        risk_level = "High Risk"
    else:
        risk_level = "Very High Risk"

    summary = report.get("summary") or "No summary available."
    if not report.get("summary"):
        summary = "This property has a moderate risk level based on available complaint and rental comparison data."

    return {
        "trust_score": score,
        "risk_level": risk_level,
        "data_confidence": report.get("data_confidence", "Low"),
        "summary": summary,
    }
