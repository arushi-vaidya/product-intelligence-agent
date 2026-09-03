import re
from urllib.parse import urlparse


def normalize_search_text(value: str) -> str:
    """Compare part numbers independently of punctuation or whitespace."""

    return re.sub(r"[^a-z0-9]", "", value.lower())


class SourceFilter:

    def filter_sources(
        self,
        sources: list[dict],
        manufacturer: str,
        mpn: str,
    ) -> list[dict]:

        filtered = []
        query_fallbacks = []
        seen_urls = set()

        manufacturer_normalized = normalize_search_text(
            manufacturer
        )
        mpn_normalized = normalize_search_text(mpn)

        for source in sources:

            url = source.get("url", "")
            title = source.get("title", "")
            snippet = source.get("snippet", "")

            if not url:
                continue

            # --------------------------------
            # 1. Deduplicate URLs
            # --------------------------------

            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)

            domain = urlparse(url).netloc.lower()
            blocked_domains = {
                "amazon.com",
                "amazon.in",
                "scribd.com",
            }

            if any(
                blocked in domain
                for blocked in blocked_domains
            ):
                continue

            # --------------------------------
            # 2. Combine searchable text
            # --------------------------------

            searchable_text = (
                f"{url} {title} {snippet}"
            ).lower()

            searchable_normalized = normalize_search_text(
                searchable_text
            )

            # --------------------------------
            # 3. Manufacturer relevance
            # --------------------------------

            manufacturer_match = (
                manufacturer_normalized
                in searchable_normalized
            )

            # --------------------------------
            # 4. Part-number relevance
            # --------------------------------

            # iC60N C20 → iC60N
            # This allows us to find pages
            # for the product family even if
            # the exact MPN is absent.

            mpn_parts = self._extract_product_terms(
                mpn
            )

            product_family_match = any(
                term in searchable_normalized
                for term in mpn_parts
            )

            exact_mpn_match = (
                bool(mpn_normalized)
                and mpn_normalized in searchable_normalized
            )

            # A full manufacturer name is often absent from a
            # distributor title/snippet. An exact MPN is a stronger
            # product identity signal, so retain that result even when
            # the manufacturer text is missing.
            if not exact_mpn_match and not (
                manufacturer_match and product_family_match
            ):
                # Tavily can return a manufacturer page with a shortened
                # title/snippet that omits the MPN. Keep it as a fallback
                # only when the query's manufacturer still matches.
                if manufacturer_match:
                    query_fallbacks.append(
                        {
                            **source,
                            "manufacturer_match": True,
                            "product_match": False,
                            "exact_mpn_match": False,
                            "search_query_match": True,
                            "domain": domain,
                        }
                    )
                continue

            # --------------------------------
            # 6. Add relevance metadata
            # --------------------------------

            source = {
                **source,
                "manufacturer_match": manufacturer_match,
                "product_match": (
                    exact_mpn_match or product_family_match
                ),
                "exact_mpn_match": exact_mpn_match,
                "domain": domain,
            }

            filtered.append(source)

        return filtered or query_fallbacks

    def _extract_product_terms(
        self,
        mpn: str,
    ) -> list[str]:

        normalized = (
            mpn.lower()
            .replace("-", " ")
            .replace("_", " ")
        )

        terms = normalized.split()

        # Keep useful terms.
        #
        # Example:
        # iC60N C20
        #
        # becomes:
        # ["ic60n", "c20"]

        return [
            term.replace(" ", "")
            for term in terms
            if len(term) >= 2
        ]
