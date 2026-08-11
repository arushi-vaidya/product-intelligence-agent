from .base import Agent, AgentInput, AgentOutput


class ConflictAgent(Agent):

    name = "conflict_agent"

    async def run(
        self,
        input: AgentInput
    ) -> AgentOutput:

        specifications = input.context.get(
            "specifications",
            {}
        )

        if not specifications:
            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "No specifications available "
                    "for conflict analysis"
                ],
            )

        conflicts = []
        resolved_specifications = {}

        # -----------------------------------
        # Analyze every specification
        # -----------------------------------

        for field, specification in specifications.items():

            evidence = specification.get(
                "evidence",
                []
            )

            # Collect unique values
            values = {}

            for item in evidence:

                value = item.get("value")

                if value is None:
                    continue

                value = str(value).strip()

                if value not in values:
                    values[value] = []

                values[value].append(item)

            # -----------------------------------
            # No usable evidence
            # -----------------------------------

            if not values:

                resolved_specifications[field] = {
                    **specification,
                    "quality_status": "unverified",
                }

                continue

            # -----------------------------------
            # Single value
            # -----------------------------------

            if len(values) == 1:

                value = next(
                    iter(values)
                )

                resolved_specifications[field] = {
                    **specification,
                    "value": value,
                    "quality_status": "consistent",
                    "source_count": len(
                        values[value]
                    ),
                }

                continue

            # -----------------------------------
            # Multiple values = conflict
            # -----------------------------------

            conflict_values = []

            for value, evidence_items in values.items():

                conflict_values.append(
                    {
                        "value": value,
                        "sources": [
                            item.get("source_id")
                            for item in evidence_items
                        ],
                    }
                )

            conflicts.append(
                {
                    "field": field,
                    "status": "conflict",
                    "values": conflict_values,
                    "reason": (
                        "Multiple distinct values "
                        "were found across sources."
                    ),
                    "requires_human_review": True,
                }
            )

            # Keep the original value for now.
            # We will resolve variants with AKGP later.

            resolved_specifications[field] = {
                **specification,
                "quality_status": "conflict",
                "conflicting_values": conflict_values,
                "requires_human_review": True,
            }

        # -----------------------------------
        # Overall quality score
        # -----------------------------------

        total_fields = len(
            specifications
        )

        conflicting_fields = len(
            conflicts
        )

        if total_fields == 0:

            quality_score = 0.0

        else:

            quality_score = round(
                (
                    total_fields
                    - conflicting_fields
                )
                / total_fields,
                2,
            )

        return AgentOutput(
            success=True,
            data={
                "specifications": (
                    resolved_specifications
                ),
                "conflicts": conflicts,
                "quality": {
                    "score": quality_score,
                    "total_fields": total_fields,
                    "conflicting_fields": (
                        conflicting_fields
                    ),
                    "requires_human_review": (
                        len(conflicts) > 0
                    ),
                },
            },
        )