from urllib.parse import quote_plus
import httpx
import re
import orjson
from .Utils import format_views

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"
yt_data_regex = re.compile(r"ytInitialData\s*=\s*(\{.+?\});", re.DOTALL)

_client = httpx.AsyncClient(
    http2=True,
    timeout=5.0,
    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
)

# ─────────────────────────────
# IN-MEMORY CACHE (FASTEST)
# ─────────────────────────────
MEMORY_CACHE = {}          # {query: output}
CACHE_LIMIT = 1000         # safety cap


async def Search(query: str, limit: int = 1):
    # ───── CACHE HIT ─────
    cached = MEMORY_CACHE.get(query)
    if cached:
        return cached

    # ───── FETCH FROM YT ─────
    url = YOUTUBE_SEARCH_URL.format(quote_plus(query))
    resp = await _client.get(url, headers=HEADERS)

    match = yt_data_regex.search(resp.text)
    if not match:
        return {"main_results": [], "suggested": []}

    data = orjson.loads(match.group(1))
    contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
        "sectionListRenderer"]["contents"]

    results = []

    for section in contents:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            v = item.get("videoRenderer")
            if not v:
                continue

            results.append({
                "title": v["title"]["runs"][0]["text"],
                "url": f"https://www.youtube.com/watch?v={v['videoId']}",
                "duration": v.get("lengthText", {}).get("simpleText", "LIVE"),
                "channel_name": v.get("ownerText", {}).get("runs", [{}])[0].get("text", "Unknown"),
                "views": format_views(v.get("viewCountText", {}).get("simpleText", "0 views")),
                "thumbnail": v["thumbnail"]["thumbnails"][-1]["url"],
            })

            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    output = {
        "main_results": results[:limit],
        "suggested": results[limit:limit + 5]
    }

    # ───── SAVE CACHE (RAM) ─────
    if len(MEMORY_CACHE) >= CACHE_LIMIT:
        MEMORY_CACHE.clear()   # simple safety
    MEMORY_CACHE[query] = output

    return output
