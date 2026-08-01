import os

from apify_client import run_actor, get_actor_run_results


def main():
    address = os.environ.get("APIFY_SEARCH_ADDRESS", "1600 Amphitheatre Parkway, Mountain View, CA")
    actor_name = "scrapeforge/facebook-search-posts"
    actor_input = {
        "search": address,
        "maxPosts": 50,
    }

    run_data = run_actor(actor_name, actor_input, timeout_seconds=180)
    run_id = run_data.get("id")
    if not run_id:
        raise RuntimeError("Failed to start Apify actor run")

    items = get_actor_run_results(run_id)
    print(items)


if __name__ == "__main__":
    main()
