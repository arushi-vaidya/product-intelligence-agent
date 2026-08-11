from .base import Agent, AgentInput, AgentOutput


class EvidenceValidationAgent(Agent):

    name = "evidence_validation_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        enrichment = input.context.get(
            "enrichment",
            {}
        )

        sources = input.context.get(
            "sources",
            []
        )

        # -----------------------------------
        # Build valid source ID set
        # -----------------------------------

        valid_source_ids = {
            source.get("id")
            for source in sources
            if source.get("id")
        }

        claims = []

        # -----------------------------------
        # Validate short description
        # -----------------------------------

        short_description = enrichment.get(
            "short_description",
            {}
        )

        if isinstance(
            short_description,
            dict
        ):

            self._validate_claim(
                claim_type="short_description",
                text=short_description.get(
                    "text"
                ),
                supported_by=short_description.get(
                    "supported_by",
                    []
                ),
                valid_source_ids=valid_source_ids,
                claims=claims,
            )

        # -----------------------------------
        # Validate features
        # -----------------------------------

        for feature in enrichment.get(
            "features",
            []
        ):

            if isinstance(
                feature,
                dict
            ):

                self._validate_claim(
                    claim_type="feature",
                    text=feature.get("text"),
                    supported_by=feature.get(
                        "supported_by",
                        []
                    ),
                    valid_source_ids=valid_source_ids,
                    claims=claims,
                )

        # -----------------------------------
        # Validate applications
        # -----------------------------------

        for application in enrichment.get(
            "applications",
            []
        ):

            if isinstance(
                application,
                dict
            ):

                self._validate_claim(
                    claim_type="application",
                    text=application.get("text"),
                    supported_by=application.get(
                        "supported_by",
                        []
                    ),
                    valid_source_ids=valid_source_ids,
                    claims=claims,
                )

        # -----------------------------------
        # Validate variants
        # -----------------------------------

        for variant in enrichment.get(
            "variant_descriptions",
            []
        ):

            if isinstance(
                variant,
                dict
            ):

                self._validate_claim(
                    claim_type="variant_description",
                    text=variant.get(
                        "description"
                    ),
                    supported_by=variant.get(
                        "supported_by",
                        []
                    ),
                    valid_source_ids=valid_source_ids,
                    claims=claims,
                    variant_mpn=variant.get(
                        "mpn"
                    ),
                )

        # -----------------------------------
        # Calculate validation statistics
        # -----------------------------------

        supported_count = sum(
            1
            for claim in claims
            if claim["status"] == "supported"
        )

        unsupported_count = sum(
            1
            for claim in claims
            if claim["status"] == "unsupported"
        )

        invalid_source_count = sum(
            1
            for claim in claims
            if claim["status"]
            == "invalid_source"
        )

        total_claims = len(claims)

        # -----------------------------------
        # Determine review requirement
        # -----------------------------------

        human_review_required = (
            unsupported_count > 0
            or invalid_source_count > 0
        )

        # -----------------------------------
        # Overall validation status
        # -----------------------------------

        if human_review_required:

            validation_status = (
                "review_required"
            )

        elif total_claims == 0:

            validation_status = (
                "no_claims"
            )

        else:

            validation_status = (
                "validated"
            )

        return AgentOutput(
            success=True,
            data={
                "evidence_validation": {

                    "status":
                        validation_status,

                    "total_claims":
                        total_claims,

                    "supported_claims":
                        supported_count,

                    "unsupported_claims":
                        unsupported_count,

                    "invalid_source_claims":
                        invalid_source_count,

                    "human_review_required":
                        human_review_required,

                    "claims":
                        claims,
                }
            },
        )

    # =====================================
    # CLAIM VALIDATION
    # =====================================

    def _validate_claim(
        self,
        claim_type,
        text,
        supported_by,
        valid_source_ids,
        claims,
        variant_mpn=None,
    ):

        if not text:

            return

        if not supported_by:

            claims.append(
                {
                    "type": claim_type,
                    "text": text,
                    "variant_mpn": variant_mpn,
                    "supported_by": [],
                    "status": "unsupported",
                    "reason": (
                        "Claim does not reference "
                        "any evidence source."
                    ),
                }
            )

            return

        invalid_sources = [
            source_id
            for source_id in supported_by
            if source_id not in valid_source_ids
        ]

        if invalid_sources:

            claims.append(
                {
                    "type": claim_type,
                    "text": text,
                    "variant_mpn": variant_mpn,
                    "supported_by": supported_by,
                    "invalid_sources": invalid_sources,
                    "status": "invalid_source",
                    "reason": (
                        "Claim references source IDs "
                        "that are not present in the "
                        "investigation."
                    ),
                }
            )

            return

        claims.append(
            {
                "type": claim_type,
                "text": text,
                "variant_mpn": variant_mpn,
                "supported_by": supported_by,
                "status": "supported",
                "reason": (
                    "Claim references valid "
                    "evidence sources."
                ),
            }
        )