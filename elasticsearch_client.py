import base64
import os

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

try:
    import requests
except ImportError:
    requests = None


def load_local_secrets() -> dict:
    """Load Streamlit secrets from .streamlit/secrets.toml when not running inside Streamlit."""
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        return {}

    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    with open(secrets_path, "rb") as f:
        return tomllib.load(f)


def get_elasticsearch_credentials():
    """Load Elasticsearch credentials from Streamlit secrets, local secrets file, or environment variables."""
    secrets = {}
    if st is not None:
        try:
            secrets = st.secrets
        except Exception:
            secrets = {}

    if not secrets:
        secrets = load_local_secrets()

    host = secrets.get("ELASTIC_HOST") or os.environ.get("ELASTIC_HOST")
    cloud_id = secrets.get("ELASTIC_CLOUD_ID") or os.environ.get("ELASTIC_CLOUD_ID")
    api_key = secrets.get("ELASTIC_API_KEY") or os.environ.get("ELASTIC_API_KEY")

    if not api_key or (not host and not cloud_id):
        raise ValueError(
            "Elasticsearch credentials are missing. Set ELASTIC_HOST or ELASTIC_CLOUD_ID plus ELASTIC_API_KEY in .streamlit/secrets.toml or environment variables."
        )

    return host, cloud_id, api_key


def parse_cloud_id(cloud_id: str) -> str:
    """Decode an Elasticsearch cloud ID into the host name."""
    if ":" not in cloud_id:
        raise ValueError("Invalid ELASTIC_CLOUD_ID format")
    _, encoded = cloud_id.split(":", 1)
    decoded = base64.b64decode(encoded).decode("utf-8")
    host = decoded.split("$")[0]
    return host


def build_elasticsearch_url(host_or_cloud_id: str) -> str:
    if host_or_cloud_id.startswith("http"):
        return host_or_cloud_id.rstrip("/")
    return f"https://{parse_cloud_id(host_or_cloud_id)}"


def get_elasticsearch_client():
    """Create an Elasticsearch client using credentials from secrets."""
    host, cloud_id, api_key = get_elasticsearch_credentials()
    if Elasticsearch is None:
        raise ImportError(
            "The elasticsearch package is not installed. Install it with pip install elasticsearch>=8.0.0 or use the HTTP fallback in test functions."
        )
    if host:
        return Elasticsearch(hosts=[host], api_key=api_key)
    return Elasticsearch(cloud_id=cloud_id, api_key=api_key)


def test_elasticsearch_connection():
    """Verify the connection to Elasticsearch and return cluster health."""
    host, cloud_id, api_key = get_elasticsearch_credentials()
    if requests is None:
        raise ImportError("The requests library is required to test Elasticsearch connection via HTTP.")

    url = build_elasticsearch_url(host or cloud_id)
    headers = {"Authorization": f"ApiKey {api_key}"}
    session = requests.Session()
    session.trust_env = False
    response = session.get(
        f"{url}/_cluster/health",
        headers=headers,
        timeout=20,
        proxies={},
    )
    response.raise_for_status()
    return response.json()


def list_elasticsearch_indexes() -> list:
    """Return a list of Elasticsearch indexes available in the connected cluster."""
    host, cloud_id, api_key = get_elasticsearch_credentials()
    if requests is None:
        raise ImportError("The requests library is required to list Elasticsearch indexes via HTTP.")

    url = build_elasticsearch_url(host or cloud_id)
    headers = {"Authorization": f"ApiKey {api_key}"}
    session = requests.Session()
    session.trust_env = False
    response = session.get(
        f"{url}/_cat/indices?h=index&format=json",
        headers=headers,
        timeout=20,
        proxies={},
    )
    response.raise_for_status()
    data = response.json()
    return sorted(item["index"] for item in data)


if __name__ == "__main__":
    info = test_elasticsearch_connection()
    print("Connected to Elasticsearch:")
    print(info)
