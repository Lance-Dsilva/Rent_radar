import streamlit as st

from demo_data import SAMPLE_REPORT
from scoring import calculate_risk_score
from services import fetch_property_data


def render_badge(text: str, color: str = "secondary") -> str:
    return f"<span style='background-color:{color}; color:#fff; padding:4px 10px; border-radius:10px; font-size:0.85em;'>{text}</span>"


def render_complaint_card(complaint: dict):
    severity_colors = {
        "Verified": "#d32f2f",
        "High": "#f57c00",
        "Medium": "#1976d2",
        "Low": "#388e3c",
    }
    color = severity_colors.get(complaint.get("severity"), "#757575")
    verified = "Verified Record" if complaint.get("verified") else "Unverified Online Report"

    st.markdown(f"### {complaint.get('category')} — {complaint.get('source')}")
    cols = st.columns([1, 1, 1])
    cols[0].markdown(f"**Severity:** {complaint.get('severity')}")
    cols[1].markdown(f"**Date:** {complaint.get('date')}")
    cols[2].markdown(f"**Status:** {verified}")
    st.markdown(f"<div style='margin: 8px 0; padding: 12px; background:#f8f8f8; border-radius:10px;'>{complaint.get('excerpt')}</div>", unsafe_allow_html=True)
    if complaint.get("link"):
        st.markdown(f"[View source]({complaint.get('link')})")
    st.markdown("---")


def render_overview(report: dict):
    st.markdown("## Overview")

    score = report.get("trust_score", 0)
    risk_level = report.get("risk_level", "Unknown")
    confidence = report.get("data_confidence", "Unknown")
    rent_diff = report.get("rent_diff_pct", 0.0)
    rent_text = f"{rent_diff:.1f}% below median" if rent_diff >= 0 else f"{abs(rent_diff):.1f}% above median"

    cols = st.columns(4)
    cols[0].metric("Rental Trust Score", f"{score}/100")
    cols[1].metric("Risk Level", risk_level)
    cols[2].metric("Data Confidence", confidence)
    cols[3].metric("Rent Difference", rent_text)

    st.markdown(f"**Property:** {report.get('property_name')}\n\n")
    st.markdown(f"**Address:** {report.get('address')}\n\n")
    st.markdown(f"**Management company:** {report.get('management_company')}\n\n")
    st.markdown(f"**Current rent:** ${report.get('current_rent'):,}  |  **Nearby median rent:** ${report.get('nearby_median_rent'):,}")
    st.markdown("---")
    st.markdown(f"**Summary:** {report.get('summary')}\n")
    st.markdown("---")


def main():
    st.set_page_config(page_title="LeaseLens", layout="wide")
    st.title("LeaseLens")
    st.write("**Know the property before you sign the lease.**")
    st.write("Enter an address and optional management company information to evaluate rental risk with demo data and external placeholder connections.")

    with st.sidebar:
        st.subheader("Property input")
        address = st.text_input("Rental address")
        management_company = st.text_input("Management company (optional)")
        property_name = st.text_input("Property name (optional)")
        use_demo = st.checkbox("Use demo data (opt-in)", value=False)
        st.markdown("---")
        st.markdown("**Demo Mode (opt-in):** When checked, the app will use bundled demo data instead of calling external services.")
        st.markdown("**Note:** Apify Actors, Elasticsearch, and LLM services must be reachable for live data.")
        submitted = st.button("Analyze Property")

    report = None
    if submitted:
        if use_demo:
            report = SAMPLE_REPORT
        elif not address:
            st.warning("Please enter a rental address or use demo mode.")
        else:
            with st.spinner("Calling Apify Facebook scraper and gathering data..."):
                report = fetch_property_data(address, management_company, property_name)

    if report:
        score_data = calculate_risk_score(report)
        report.update(score_data)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Complaints", "Landlord History", "Nearby Rentals", "Evidence", "Social Media"])

        with tab1:
            render_overview(report)

        with tab2:
            st.markdown("## Complaints")
            if report.get("complaints"):
                for complaint in report["complaints"]:
                    render_complaint_card(complaint)
            else:
                st.info("No complaint data is available for this property.")

        with tab3:
            st.markdown("## Landlord History")
            if report.get("landlord_history"):
                for record in report["landlord_history"]:
                    st.markdown(f"**{record.get('property')}** — {record.get('city')} | {record.get('issues')} issues detected")
                    st.markdown(f"- Complaint count: {record.get('complaint_count')}\n- Most recent: {record.get('last_reported')}")
                    st.markdown("---")
            else:
                st.info("No landlord history data is available.")

        with tab4:
            st.markdown("## Nearby Rentals")
            nearby = report.get("nearby_rentals", [])
            if nearby:
                st.dataframe(nearby)
                chart_data = {item["name"]: item["rent"] for item in nearby}
                st.bar_chart(chart_data)
            else:
                st.info("Nearby rental comparisons are unavailable.")

        with tab5:
            st.markdown("## Evidence")
            if report.get("evidence"):
                for item in report["evidence"]:
                    st.markdown(f"- **{item.get('title')}** ({item.get('source')}) — {item.get('note')}")
            else:
                st.info("No evidence sources are available.")

        with tab6:
            st.markdown("## Facebook Scraper Results")
            if report.get("facebook_posts"):
                for post in report["facebook_posts"][:10]:
                    st.markdown(f"**{post.get('title', 'Facebook post')}**")
                    st.markdown(f"- Date: {post.get('date', 'N/A')}\n- URL: {post.get('url', 'N/A')}\n- Text: {post.get('text', '')[:200]}")
                    st.markdown("---")
            else:
                st.info("No Facebook scraper results are available.")

    else:
        st.info("Enter a rental address and click Analyze Property to see the LeaseLens report.")


if __name__ == "__main__":
    main()
