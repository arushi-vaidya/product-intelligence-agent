import json
import os

from dotenv import load_dotenv
from google import genai

from .base import Agent, AgentInput, AgentOutput


load_dotenv()


class EnrichmentAgent(Agent):

    name = "enrichment_agent"

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

        canonical_product = input.context.get(
            "canonical_product",
            {}
        )

        sources = input.context.get(
            "sources",
            []
        )

        # -----------------------------------
        # Build evidence context
        # -----------------------------------

        evidence = []

        # Source-level evidence
        for source in sources:

            evidence.append({
                "source_id": source.get("id"),
                "title": source.get("title"),
                "url": source.get("url"),
                "snippet": source.get(
                    "snippet",
                    ""
                ),
            })

        # -----------------------------------
        # Add specification-level evidence
        # -----------------------------------

        specification_evidence = {}

        family_specifications = (
            canonical_product.get(
                "family_specifications",
                {}
            )
        )

        for field, specification in (
            family_specifications.items()
        ):

            specification_evidence[
                field
            ] = specification.get(
                "evidence",
                []
            )

        # -----------------------------------
        # Build LLM prompt
        # -----------------------------------

        prompt = f"""
You are an industrial product data enrichment agent.

Your job is to create commerce-ready product content
from VERIFIED product intelligence.

You MUST ground every factual claim in the supplied
canonical product data or evidence.

PRODUCT:

Manufacturer:
{manufacturer}

MPN:
{mpn}

CANONICAL PRODUCT:
{json.dumps(
    canonical_product,
    indent=2
)}

SOURCE EVIDENCE:
{json.dumps(
    evidence,
    indent=2
)}

SPECIFICATION EVIDENCE:
{json.dumps(
    specification_evidence,
    indent=2
)}

IMPORTANT RULES:

1. Do NOT invent technical specifications.

2. Do NOT guess missing values.

3. Do NOT infer technical properties from incomplete
   information.

4. Every factual feature MUST reference one or more
   source IDs from the supplied evidence.

5. Every factual application MUST reference one or more
   source IDs from the supplied evidence.

6. Technical summary values MUST be supported by the
   canonical product.

7. Keep family-level specifications separate from
   variant-specific specifications.

8. Do NOT apply a family-level specification to a
   variant unless the evidence explicitly supports it.

9. Do NOT infer electrical characteristics such as
   phase configuration, voltage, compatibility,
   installation type, or application merely from
   pole count or product name.

10. If there is insufficient evidence for a claim,
    omit the claim.

11. Only use source IDs that actually appear in the
    supplied evidence.

12. Keep descriptions concise and factual.

13. Search keywords may include manufacturer, product
    family, MPN, category, and explicitly supported
    technical terms.

14. Do NOT put unsupported claims into search keywords.

15. Return ONLY valid JSON.

Return exactly this structure:

{{
    "title": "...",

    "short_description": {{
        "text": "...",
        "supported_by": []
    }},

    "features": [
        {{
            "text": "...",
            "supported_by": []
        }}
    ],

    "applications": [
        {{
            "text": "...",
            "supported_by": []
        }}
    ],

    "search_keywords": [],

    "technical_summary": {{}},

    "variant_descriptions": [
        {{
            "mpn": "...",
            "description": "...",
            "supported_by": []
        }}
    ]
}}

IMPORTANT:

The "supported_by" arrays must contain ONLY valid
source IDs from the supplied evidence.

Example:

{{
    "text": "Provides protection against overload currents.",
    "supported_by": ["src_1"]
}}

If a claim cannot be supported, DO NOT generate it.
"""

        # -----------------------------------
        # Call Gemini
        # -----------------------------------

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            return AgentOutput(
                success=False,
                data={},
                errors=[
                    "GEMINI_API_KEY is not configured"
                ],
            )

        try:

            client = genai.Client(
                api_key=api_key
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            raw_text = (
                response.text.strip()
            )

            # -----------------------------------
            # Remove markdown fences
            # -----------------------------------

            if raw_text.startswith(
                "```json"
            ):

                raw_text = (
                    raw_text
                    .replace(
                        "```json",
                        "",
                        1
                    )
                    .replace(
                        "```",
                        "",
                        1
                    )
                    .strip()
                )

            elif raw_text.startswith(
                "```"
            ):

                raw_text = (
                    raw_text
                    .replace(
                        "```",
                        "",
                        1
                    )
                    .strip()
                )

            # -----------------------------------
            # Parse JSON
            # -----------------------------------

            enrichment = json.loads(
                raw_text
            )

        except Exception as error:

            return AgentOutput(
                success=False,
                data={},
                errors=[
                    f"LLM enrichment failed: {error}"
                ],
            )

        # -----------------------------------
        # Return
        # -----------------------------------

        return AgentOutput(
            success=True,
            data={
                "enrichment": enrichment,
                "model": "gemini-2.5-flash",
            },
        )