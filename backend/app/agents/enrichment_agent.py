import json
import os

from google import genai

from .base import Agent, AgentInput, AgentOutput
from dotenv import load_dotenv

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

        for source in sources:

            evidence.append({
                "source_id": source.get("id"),
                "title": source.get("title"),
                "url": source.get("url"),
                "snippet": source.get("snippet", "")
            })

        # -----------------------------------
        # Build LLM prompt
        # -----------------------------------

        prompt = f"""
You are an industrial product data enrichment agent.

Your job is to create commerce-ready product content
from VERIFIED product intelligence.

PRODUCT:

Manufacturer:
{manufacturer}

MPN:
{mpn}

CANONICAL PRODUCT:
{json.dumps(canonical_product, indent=2)}

AVAILABLE SOURCES:
{json.dumps(evidence, indent=2)}

RULES:

1. Do NOT invent technical specifications.
2. Do NOT guess missing values.
3. Only mention technical facts supported by the
   canonical product or supplied evidence.
4. Keep family-level specifications separate from
   variant-specific specifications.
5. Generate useful commerce-oriented language.
6. Product descriptions should be concise and factual.
7. If an application is not explicitly supported,
   phrase it cautiously or omit it.
8. Return ONLY valid JSON.

Return this exact structure:

{{
    "title": "...",
    "short_description": "...",
    "features": [],
    "applications": [],
    "search_keywords": [],
    "technical_summary": {{}},
    "variant_descriptions": []
}}
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

            raw_text = response.text.strip()

            # Remove markdown fences if model
            # happens to return them.

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