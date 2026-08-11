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

            extraction_method = document.get(
                "extraction_method"
            )

            self._extract_rated_current(
                text,
                source_id,
                extraction_method,
                specifications,
            )

            self._extract_poles(
                text,
                source_id,
                extraction_method,
                specifications,
            )

            self._extract_trip_curve(
                text,
                source_id,
                extraction_method,
                specifications,
            )

            self._extract_frequency(
                text,
                source_id,
                extraction_method,
                specifications,
            )

            self._extract_breaking_capacity(
                text,
                source_id,
                extraction_method,
                specifications,
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
            specifications,
            "poles",
            value=value,
            unit=None,
            source_id=source_id,
            extraction_method=extraction_method,
            text=match.group(0),
        )

    # =====================================
    # TRIP CURVE
    # =====================================

    def _extract_trip_curve(
        self,
        text,
        source_id,
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
            specifications,
            "trip_curve",
            value=value,
            unit=None,
            source_id=source_id,
            extraction_method=extraction_method,
            text=match.group(0),
        )

    # =====================================
    # FREQUENCY
    # =====================================

    def _extract_frequency(
        self,
        text,
        source_id,
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
            specifications,
            "frequency",
            value=value,
            unit="Hz",
            source_id=source_id,
            extraction_method=extraction_method,
            text=match.group(0),
        )

    # =====================================
    # BREAKING CAPACITY
    # =====================================

    def _extract_breaking_capacity(
        self,
        text,
        source_id,
        extraction_method,
        specifications,
    ):

        patterns = [
            r"(\d+(?:\.\d+)?)\s*kA",
            r"breaking\s+capacity.{0,40}?"
            r"(\d+(?:\.\d+)?)\s*kA",
        ]

        self._extract_with_patterns(
            text=text,
            patterns=patterns,
            field="breaking_capacity",
            unit="kA",
            source_id=source_id,
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
                specifications,
                field,
                value=value,
                unit=unit,
                source_id=source_id,
                extraction_method=extraction_method,
                text=match.group(0),
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
        extraction_method,
        text,
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

        specifications[field]["evidence"].append(
            {
                "source_id": source_id,
                "value": value,
                "unit": unit,
                "text": text,
                "extraction_method": extraction_method,
            }
        )

    def _initial_confidence(
        self,
        extraction_method
    ) -> float:

        if extraction_method == "direct_http":
            return 0.95

        if extraction_method == "research_snippet":
            return 0.80

        return 0.70