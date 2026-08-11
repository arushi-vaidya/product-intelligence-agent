import re

from .base import Agent, AgentInput, AgentOutput


class SpecificationAgent(Agent):

    name = "specification_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        documents = input.context.get(
            "documents",
            []
        )

        manufacturer = input.context.get(
            "manufacturer"
        )

        mpn = input.context.get(
            "mpn"
        )

        if not documents:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "No documents available "
                    "for specification extraction"
                ],
            )

        specifications = {}

        for document in documents:

            text = document.get(
                "text",
                ""
            )

            if not text:
                continue

            source_id = document.get(
                "source_id"
            )

            source_url = document.get(
                "url"
            )

            source_title = document.get(
                "title"
            )

            extraction_method = document.get(
                "extraction_method"
            )

            # -----------------------------------
            # Rated Current
            # -----------------------------------

            self._extract_rated_current(
                text=text,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                specifications=specifications,
            )

            # -----------------------------------
            # Poles
            # -----------------------------------

            self._extract_poles(
                text=text,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                specifications=specifications,
            )

            # -----------------------------------
            # Trip Curve
            # -----------------------------------

            self._extract_trip_curve(
                text=text,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                specifications=specifications,
            )

            # -----------------------------------
            # Frequency
            # -----------------------------------

            self._extract_frequency(
                text=text,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                specifications=specifications,
            )

            # -----------------------------------
            # Breaking Capacity
            # -----------------------------------

            self._extract_breaking_capacity(
                text=text,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                specifications=specifications,
            )

        return AgentOutput(
            success=True,
            data={
                "product": {
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                },
                "specifications": specifications,
            },
        )

    # =====================================
    # RATED CURRENT
    # =====================================

    def _extract_rated_current(
        self,
        text,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        patterns = [
            r"rated\s+current.{0,30}?(\d+(?:\.\d+)?)\s*A",
            r"(\d+(?:\.\d+)?)\s*A\s*(?:rated|current)",
            r"\b(\d+(?:\.\d+)?)\s*A\b",
        ]

        self._extract_with_patterns(
            text=text,
            patterns=patterns,
            field="rated_current",
            unit="A",
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            extraction_method=extraction_method,
            specifications=specifications,
        )

    # =====================================
    # POLES
    # =====================================

    def _extract_poles(
        self,
        text,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        match = re.search(
            r"\b([1-4])P\b",
            text,
            re.IGNORECASE,
        )

        if not match:
            return

        value = match.group(1) + "P"

        self._add_evidence(
            specifications=specifications,
            field="poles",
            value=value,
            unit=None,
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            extraction_method=extraction_method,
            matched_text=match.group(0),
            source_text=text,
        )

    # =====================================
    # TRIP CURVE
    # =====================================

    def _extract_trip_curve(
        self,
        text,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        match = re.search(
            r"(?:curve|characteristic)"
            r".{0,20}?\b([B,C,D])\b",
            text,
            re.IGNORECASE,
        )

        if not match:
            return

        value = match.group(1).upper()

        self._add_evidence(
            specifications=specifications,
            field="trip_curve",
            value=value,
            unit=None,
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            extraction_method=extraction_method,
            matched_text=match.group(0),
            source_text=text,
        )

    # =====================================
    # FREQUENCY
    # =====================================

    def _extract_frequency(
        self,
        text,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        match = re.search(
            r"(\d+(?:/\d+)?)\s*Hz",
            text,
            re.IGNORECASE,
        )

        if not match:
            return

        value = match.group(1)

        self._add_evidence(
            specifications=specifications,
            field="frequency",
            value=value,
            unit="Hz",
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            extraction_method=extraction_method,
            matched_text=match.group(0),
            source_text=text,
        )

    # =====================================
    # BREAKING CAPACITY
    # =====================================

    def _extract_breaking_capacity(
        self,
        text,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        patterns = [
            r"breaking\s+capacity.{0,40}?"
            r"(\d+(?:\.\d+)?)\s*kA",

            r"(\d+(?:\.\d+)?)\s*kA",
        ]

        self._extract_with_patterns(
            text=text,
            patterns=patterns,
            field="breaking_capacity",
            unit="kA",
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            extraction_method=extraction_method,
            specifications=specifications,
        )

    # =====================================
    # GENERIC EXTRACTION
    # =====================================

    def _extract_with_patterns(
        self,
        text,
        patterns,
        field,
        unit,
        source_id,
        source_url,
        source_title,
        extraction_method,
        specifications,
    ):

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = match.group(1)

            self._add_evidence(
                specifications=specifications,
                field=field,
                value=value,
                unit=unit,
                source_id=source_id,
                source_url=source_url,
                source_title=source_title,
                extraction_method=extraction_method,
                matched_text=match.group(0),
                source_text=text,
            )

            return

    # =====================================
    # EVIDENCE
    # =====================================

    def _add_evidence(
        self,
        specifications,
        field,
        value,
        unit,
        source_id,
        source_url,
        source_title,
        extraction_method,
        matched_text,
        source_text,
    ):

        if field not in specifications:

            specifications[field] = {
                "value": value,
                "unit": unit,
                "confidence": self._initial_confidence(
                    extraction_method
                ),
                "evidence": [],
            }

        evidence_text = (
            self._get_evidence_context(
                source_text=source_text,
                matched_text=matched_text,
            )
        )

        specifications[field][
            "evidence"
        ].append(
            {
                "source_id": source_id,

                "source_url": source_url,

                "source_title": source_title,

                "value": value,

                "unit": unit,

                "text": evidence_text,

                "extraction_method": (
                    extraction_method
                ),
            }
        )

    # =====================================
    # EVIDENCE CONTEXT
    # =====================================

    def _get_evidence_context(
        self,
        source_text: str,
        matched_text: str,
        window: int = 150,
    ) -> str:

        if not source_text:
            return matched_text

        index = source_text.lower().find(
            matched_text.lower()
        )

        if index == -1:
            return matched_text

        start = max(
            0,
            index - window
        )

        end = min(
            len(source_text),
            index
            + len(matched_text)
            + window
        )

        context = source_text[
            start:end
        ].strip()

        # Clean excessive whitespace
        context = re.sub(
            r"\s+",
            " ",
            context,
        )

        return context

    # =====================================
    # CONFIDENCE
    # =====================================

    def _initial_confidence(
        self,
        extraction_method
    ) -> float:

        if extraction_method == "direct_http":
            return 0.95

        if extraction_method == "research_snippet":
            return 0.80

        return 0.70