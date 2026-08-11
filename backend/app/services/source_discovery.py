import os
from typing import List

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


class SourceDiscoveryService:

    def __init__(self):

        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY is not configured"
            )

        self.client = TavilyClient(
            api_key=api_key
        )

    async def search_product(
        self,
        manufacturer: str,
        mpn: str,
    ) -> List[dict]:

        query = f'"{manufacturer}" "{mpn}"'

        print(
            f"[SOURCE DISCOVERY] Searching: {query}"
        )

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=8,
        )

        results = response.get(
            "results",
            []
        )

        sources = []

        for index, result in enumerate(results):

            url = result.get("url")
            title = result.get("title")
            content = result.get("content")

            if not url:
                continue

            source_type = self._classify_source(
                url=url,
                title=title or "",
            )

            authority_tier = (
                self._get_authority_tier(
                    source_type
                )
            )

            sources.append(
                {
                    "id": f"src_{index + 1}",
                    "url": url,
                    "source_type": source_type,
                    "authority_tier": authority_tier,
                    "title": title,
                    "snippet": content,
                }
            )

        print(
            f"[SOURCE DISCOVERY] "
            f"Found {len(sources)} sources"
        )

        return sources

    def _classify_source(
        self,
        url: str,
        title: str,
    ) -> str:

        url_lower = url.lower()
        title_lower = title.lower()

        if url_lower.endswith(".pdf"):
            return "manufacturer_datasheet"

        if (
            "datasheet" in title_lower
            or "data sheet" in title_lower
            or "manual" in title_lower
        ):
            return "technical_document"

        if any(
            keyword in url_lower
            for keyword in [
                "schneider-electric",
                "se.com",
            ]
        ):
            return "manufacturer_page"

        if any(
            keyword in title_lower
            for keyword in [
                "distributor",
                "electrical",
                "industrial",
            ]
        ):
            return "distributor"

        return "other"

    def _get_authority_tier(
        self,
        source_type: str,
    ) -> int:

        authority = {
            "manufacturer_datasheet": 1,
            "manufacturer_page": 1,
            "technical_document": 1,
            "distributor": 2,
            "other": 3,
        }

        return authority.get(
            source_type,
            3
        )