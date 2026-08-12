import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_IMAGE_BYTES = 10 * 1024 * 1024

EXTRACTION_PROMPT = """
You are analyzing an image of an industrial or electrical product.

Extract the manufacturer name and product identifier visible on the product,
label, packaging, or nameplate.

Return ONLY valid JSON in this exact shape:
{
  "manufacturer": "string or null",
  "mpn": "string or null",
  "notes": "brief optional note about what you read"
}

Rules:
- manufacturer: the company or brand name
- mpn: the most specific product identifier available
  (catalog number, MPN, model number, or part number)
- Use null when a field is not visible or cannot be determined
- Do not invent information that is not supported by the image
- Prefer exact text from labels over guesses
"""


class ProductImageExtractionError(Exception):
    pass


def extract_product_from_image(
    image_bytes: bytes,
    mime_type: str,
) -> dict[str, str | None]:
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ProductImageExtractionError(
            "Unsupported image type. Use JPEG, PNG, WebP, or GIF."
        )

    if not image_bytes:
        raise ProductImageExtractionError(
            "Uploaded image is empty."
        )

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ProductImageExtractionError(
            "Image is too large. Maximum size is 10 MB."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ProductImageExtractionError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            EXTRACTION_PROMPT,
        ],
    )

    raw_text = (response.text or "").strip()

    if not raw_text:
        raise ProductImageExtractionError(
            "Gemini did not return any extraction result."
        )

    parsed = _parse_json_response(raw_text)

    manufacturer = _clean_value(
        parsed.get("manufacturer")
    )
    mpn = _clean_value(parsed.get("mpn"))
    notes = _clean_value(parsed.get("notes"))

    if not manufacturer and not mpn:
        detail = notes or (
            "Could not identify a manufacturer or product "
            "identifier in the image."
        )

        raise ProductImageExtractionError(detail)

    return {
        "manufacturer": manufacturer,
        "mpn": mpn,
        "notes": notes,
    }


def _clean_value(
    value: object,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    cleaned = value.strip()

    if not cleaned or cleaned.lower() in {
        "null",
        "none",
        "unknown",
        "n/a",
    }:
        return None

    return cleaned


def _parse_json_response(
    raw_text: str,
) -> dict[str, object]:
    cleaned = raw_text.strip()

    if cleaned.startswith("```json"):
        cleaned = (
            cleaned
            .replace("```json", "", 1)
            .replace("```", "", 1)
            .strip()
        )
    elif cleaned.startswith("```"):
        cleaned = (
            cleaned
            .replace("```", "", 1)
            .strip()
        )

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL,
    )

    if match:
        try:
            parsed = json.loads(match.group(0))

            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    raise ProductImageExtractionError(
        "Gemini returned an invalid extraction response."
    )
