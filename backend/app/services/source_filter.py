from urllib.parse import urlparse


class SourceFilter:

    def filter_sources(
        self,
        sources: list[dict],
        manufacturer: str,
        mpn: str,
    ) -> list[dict]:

        filtered = []
        seen_urls = set()

        manufacturer_normalized = (
            manufacturer.lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

        mpn_normalized = mpn.lower().replace(" ", "")

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

            # --------------------------------
            # 2. Combine searchable text
            # --------------------------------

            searchable_text = (
                f"{url} {title} {snippet}"
            ).lower()

            searchable_normalized = (
                searchable_text
                .replace(" ", "")
                .replace("-", "")
                .replace("_", "")
            )

            # --------------------------------
            # 3. Manufacturer relevance
            # --------------------------------

            manufacturer_match = (
                manufacturer_normalized
                in searchable_normalized
            )

            if not manufacturer_match:
                continue

            # --------------------------------
            # 4. Product-family relevance
            # --------------------------------

            # iC60N C20 → iC60N
            # This allows us to find pages
            # for the product family even if
            # the exact MPN is absent.

            mpn_parts = self._extract_product_terms(
                mpn
            )

            product_match = any(
                term in searchable_normalized
                for term in mpn_parts
            )

            if not product_match:
                continue

            # --------------------------------
            # 5. Reject obvious low-value
            # sources
            # --------------------------------

            domain = (
                urlparse(url)
                .netloc
                .lower()
            )

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
            # 6. Add relevance metadata
            # --------------------------------

            source = {
                **source,
                "manufacturer_match": True,
                "product_match": True,
                "domain": domain,
            }

            filtered.append(source)

        return filtered

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