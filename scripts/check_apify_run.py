import time
import requests
import os
from apify_client import get_apify_token

run_id = 'C1iACg20X0vJC7f7V'
actor_url = 'https://api.apify.com/v2/acts/scrapeforge~facebook-search-posts/runs'
status_url = f"{actor_url}/{run_id}"

print('Polling run', run_id)
deadline = time.time() + 180
status = None
session = requests.Session()
session.trust_env = False

try:
    token = get_apify_token()
except Exception:
    token = os.environ.get('APIFY_TOKEN')

if not token:
    print('APIFY token not found in environment or local secrets. Set APIFY_TOKEN to run this script.')
    raise SystemExit(1)

while time.time() < deadline:
    r = session.get(status_url, params={'token': token}, timeout=30, proxies={})
    try:
        r.raise_for_status()
    except Exception:
        print('Status request failed:', getattr(r, 'status_code', None), getattr(r, 'text', '')[:200])
        break
    j = r.json()
    status = j.get('status') or (j.get('data') or {}).get('status')
    print('status =', status)
    if status in ('SUCCEEDED', 'FAILED', 'ABORTED'):
        break
    time.sleep(3)

if status != 'SUCCEEDED':
    print('Run did not succeed or could not be polled. Final status:', status)
else:
    data_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    r = session.get(data_url, params={'token': token, 'limit': 10}, timeout=30, proxies={})
    r.raise_for_status()
    items = r.json()
    print('Got', len(items), 'items')
    for i, it in enumerate(items):
        print('--- item', i, '---')
        for k, v in list(it.items())[:8]:
            print(k + ':', str(v)[:500])

print('Done')
