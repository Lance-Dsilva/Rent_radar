import os
import time
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
except ImportError:
    st = None

import requests


def load_local_secrets() -> dict:
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        return {}

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    with open(secrets_path, "rb") as f:
        return tomllib.load(f)


def get_apify_token() -> str:
    secrets = {}
    if st is not None:
        try:
            secrets = st.secrets
        except Exception:
            secrets = {}

    if not secrets:
        secrets = load_local_secrets()

    token = secrets.get("APIFY_TOKEN") or os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("Apify token is missing. Set APIFY_TOKEN in .streamlit/secrets.toml or environment variables.")

    return token


def normalize_actor_name(actor_name: str) -> str:
    return actor_name.replace("/", "~")


def build_actor_runs_url(actor_name: str) -> str:
    normalized_actor = normalize_actor_name(actor_name)
    return f"https://api.apify.com/v2/acts/{normalized_actor}/runs"


def run_actor(actor_name: str, actor_input: Dict[str, Any], timeout_seconds: int = 120) -> Dict[str, Any]:
    token = get_apify_token()
    url = build_actor_runs_url(actor_name)
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, params={"token": token}, json=actor_input, timeout=30, proxies={})
    response.raise_for_status()
    run_body = response.json()

    # Apify sometimes returns {"data": {...}} and sometimes top-level fields.
    run_data = run_body.get("data") or run_body
    run_id = run_data.get("id")
    if not run_id:
        raise RuntimeError("Failed to start Apify actor run: missing run ID.")

    run_status_url = f"{url}/{run_id}"
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_response = session.get(run_status_url, params={"token": token}, timeout=30, proxies={})
        status_response.raise_for_status()
        status_body = status_response.json()
        status_data = status_body.get("data") or status_body
        status = status_data.get("status")
        if status in {"SUCCEEDED", "FAILED", "ABORTED"}:
            # Return a stable dict with an `id` key and the raw status payload
            result = {"id": run_id, "status": status}
            result.update(status_data)
            result["raw"] = status_body
            return result
        time.sleep(3)

    raise TimeoutError("Apify actor run did not finish within the configured timeout.")


def get_actor_run_results(run_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    token = get_apify_token()
    session = requests.Session()
    session.trust_env = False
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    response = session.get(url, params={"token": token, "limit": limit}, timeout=30, proxies={})
    response.raise_for_status()
    items = response.json()
    # Ensure a list is returned
    if isinstance(items, dict) and "data" in items:
        return items.get("data") or []
    if isinstance(items, list):
        return items
    return []
