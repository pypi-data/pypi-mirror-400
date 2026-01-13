from urllib.parse import quote_plus
import httpx
import re
import orjson
import redis.asyncio as redis
from .Utils import format_views

r = redis.Redis(host='localhost', port=6379, db=0)
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={}"
yt_data_regex = re.compile(r"ytInitialData\s*=\s*(\{.+?\});", re.DOTALL)
_client = httpx.AsyncClient(http2=True, timeout=5.0, limits=httpx.Limits(max_connections=10, max_keepalive_connections=5))

async def Search(query: str, limit: int = 1):
    cached = await r.get(query)
    if cached:
        return orjson.loads(cached)

    search_url = YOUTUBE_SEARCH_URL.format(quote_plus(query))
    response = await _client.get(search_url, headers=HEADERS)
    match = yt_data_regex.search(response.text)
    if not match:
        return {"main_results": [], "suggested": []}

    data = orjson.loads(match.group(1))
    results = []
    sections = data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])

    for section in sections:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            if "videoRenderer" in item:
                v = item["videoRenderer"]
                results.append({
                    "type": "video",
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

    output = {"main_results": results[:limit], "suggested": results[limit:limit + 5]}
    await r.set(query, orjson.dumps(output))
    return output
