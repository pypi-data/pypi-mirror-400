from typing import cast

from yarl import URL

from raphson_mp.common import httpclient
from raphson_mp.server import ratelimit


async def get_url_from_wikidata(wikidata_id: str) -> str | None:
    """
    Returns: wikipedia URL like https://en.wikipedia.org/wiki/Green_Day
    """
    async with ratelimit.WIKIDATA:
        async with httpclient.session() as session:
            async with session.get(
                f"https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/{wikidata_id}/sitelinks",
                raise_for_status=False,
            ) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                return cast(str, data["enwiki"]["url"]) if "enwiki" in data else None


async def get_wikipedia_extract(wikipedia_url: str) -> str:
    parsed_url = URL(wikipedia_url)

    # Example: https://en.wikipedia.org/api/rest_v1/page/summary/Green_Day
    api_url = f"https://{parsed_url.authority}/api/rest_v1/page/summary/{parsed_url.path.removeprefix('/wiki/')}"

    async with ratelimit.WIKIPEDIA:
        async with httpclient.session() as session:
            async with session.get(api_url) as response:
                data = await response.json()

    return cast(str, data["extract"])
