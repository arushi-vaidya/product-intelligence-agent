from .base import Agent, AgentInput, AgentOutput


class SourceValidationAgent(Agent):

    name = "source_validation_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        manufacturer = input.context.get(
            "manufacturer"
        )

        mpn = input.context.get(
            "mpn"
        )

        sources = input.context.get(
            "sources",
            []
        )

        if not manufacturer or not mpn:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "Manufacturer and MPN are required"
                ],
            )

        if not sources:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "No candidate sources available"
                ],
            )

        validated_sources = []

        for source in sources:

            validation = self._validate_source(
                source=source,
                manufacturer=manufacturer,
                mpn=mpn,
            )

            validated_sources.append(
                {
                    **source,
                    "validation": validation,
                }
            )

        valid_sources = [
            source
            for source in validated_sources
            if source["validation"]["is_valid"]
        ]

        return AgentOutput(
            success=True,
            data={
                "manufacturer": manufacturer,
                "mpn": mpn,
                "validated_sources": valid_sources,
                "rejected_sources": [
                    source
                    for source in validated_sources
                    if not source["validation"]["is_valid"]
                ],
            },
        )

    def _validate_source(
        self,
        source: dict,
        manufacturer: str,
        mpn: str,
    ) -> dict:

        title = (
            source.get("title") or ""
        )

        snippet = (
            source.get("snippet") or ""
        )

        url = (
            source.get("url") or ""
        )

        text = (
            f"{title} {snippet} {url}"
        ).lower()

        manufacturer_match = (
            manufacturer.lower()
            in text
        )

        normalized_mpn = (
            mpn.lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

        normalized_text = (
            text
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

        exact_mpn_match = (
            normalized_mpn
            in normalized_text
        )

        product_family_match = False

        # For "iC60N C20", identify "iC60N"
        # as the product-family term.

        mpn_parts = mpn.split()

        if mpn_parts:

            family = (
                mpn_parts[0]
                .lower()
            )

            product_family_match = (
                family in normalized_text
            )

        authority_tier = source.get(
            "authority_tier",
            3,
        )

        score = 0.0

        if manufacturer_match:
            score += 0.30

        if exact_mpn_match:
            score += 0.45

        elif product_family_match:
            score += 0.25

        if authority_tier == 1:
            score += 0.20

        elif authority_tier == 2:
            score += 0.10

        score = min(score, 1.0)

        is_valid = (
            manufacturer_match
            and (
                exact_mpn_match
                or product_family_match
            )
            and score >= 0.50
        )

        evidence = []

        if manufacturer_match:
            evidence.append(
                "Manufacturer match"
            )

        if exact_mpn_match:
            evidence.append(
                "Exact MPN match"
            )

        elif product_family_match:
            evidence.append(
                "Product family match"
            )

        if authority_tier == 1:
            evidence.append(
                "High-authority source"
            )

        return {
            "is_valid": is_valid,
            "match_score": round(score, 2),
            "evidence": evidence,
        }