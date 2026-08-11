import io

import httpx
from pypdf import PdfReader

from .base import Agent, AgentInput, AgentOutput


class DocumentAgent(Agent):

    name = "document_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        sources = input.context.get(
            "validated_sources",
            []
        )

        if not sources:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "No validated sources available"
                ],
            )

        documents = []
        failed_sources = []

        for source in sources:

            url = source.get("url")

            if not url:
                continue

            print(
                f"[DOCUMENT] Fetching: {url}"
            )

            try:

                document = await self._fetch_source(
                    source
                )

                if document:
                    documents.append(document)

            except Exception as error:

                print(
                    f"[DOCUMENT] Failed to fetch "
                    f"{url}: {error}"
                )

                # --------------------------------
                # FALLBACK
                # --------------------------------

                fallback_document = (
                    self._create_fallback_document(
                        source
                    )
                )

                if fallback_document:
                    documents.append(
                        fallback_document
                    )

                failed_sources.append(
                    {
                        "source_id": source.get("id"),
                        "url": url,
                        "error": str(error),
                    }
                )

        # --------------------------------
        # We only fail if we have absolutely
        # no usable evidence.
        # --------------------------------

        if not documents:

            return AgentOutput(
                success=False,
                data={
                    "documents": [],
                    "failed_sources": failed_sources,
                },
                errors=[
                    "Could not extract or recover "
                    "any source content"
                ],
            )

        return AgentOutput(
            success=True,
            data={
                "documents": documents,
                "failed_sources": failed_sources,
            },
        )

    # =======================================
    # DIRECT SOURCE FETCH
    # =======================================

    async def _fetch_source(
        self,
        source: dict
    ) -> dict | None:

        url = source["url"]

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Product Intelligence MVP)"
                )
            },
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

        content_type = (
            response.headers
            .get("content-type", "")
            .lower()
        )

        # --------------------------------
        # PDF
        # --------------------------------

        if (
            "application/pdf" in content_type
            or url.lower().endswith(".pdf")
        ):

            return self._extract_pdf(
                source,
                response.content
            )

        # --------------------------------
        # HTML
        # --------------------------------

        if "text/html" in content_type:

            text = self._extract_html(
                response.text
            )

            return {
                "source_id": source.get("id"),
                "url": url,
                "title": source.get("title"),
                "document_type": "html",
                "extraction_method": "direct_http",
                "text": text,
            }

        # --------------------------------
        # Unknown content
        # --------------------------------

        return {
            "source_id": source.get("id"),
            "url": url,
            "title": source.get("title"),
            "document_type": "unknown",
            "extraction_method": "direct_http",
            "text": response.text[:50000],
        }

    # =======================================
    # FALLBACK
    # =======================================

    def _create_fallback_document(
        self,
        source: dict
    ) -> dict | None:

        snippet = source.get(
            "snippet",
            ""
        )

        if not snippet:
            return None

        print(
            f"[DOCUMENT] Using research snippet "
            f"fallback for {source.get('id')}"
        )

        return {
            "source_id": source.get("id"),
            "url": source.get("url"),
            "title": source.get("title"),
            "document_type": "source_evidence",
            "extraction_method": "research_snippet",
            "text": snippet,
        }

    # =======================================
    # PDF EXTRACTION
    # =======================================

    def _extract_pdf(
        self,
        source: dict,
        content: bytes
    ) -> dict:

        reader = PdfReader(
            io.BytesIO(content)
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text() or ""

            if text.strip():

                pages.append(
                    {
                        "page": page_number,
                        "text": text,
                    }
                )

        combined_text = "\n\n".join(
            page["text"]
            for page in pages
        )

        return {
            "source_id": source.get("id"),
            "url": source.get("url"),
            "title": source.get("title"),
            "document_type": "pdf",
            "extraction_method": "direct_http",
            "page_count": len(reader.pages),
            "pages": pages,
            "text": combined_text,
        }

    # =======================================
    # HTML EXTRACTION
    # =======================================

    def _extract_html(
        self,
        html: str
    ) -> str:

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        return soup.get_text(
            separator=" ",
            strip=True
        )[:50000]