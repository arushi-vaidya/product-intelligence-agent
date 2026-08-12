# Industrial Product Intelligence — Backend

AI-powered backend for researching, validating, resolving, and enriching industrial product information.

The backend takes a manufacturer and product/MPN as input and runs it through a multi-agent investigation pipeline to produce structured, commerce-ready product intelligence.

---

## Overview

The backend is built around a DFOO orchestration pipeline.

```text
                    ┌─────────────────────┐
                    │   Product Request    │
                    │ Manufacturer + MPN   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Intake Agent     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Research Agent    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Source Validation   │
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Document Agent    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Specification Agent │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Conflict Agent     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    AKGP Agent       │
                    │ Knowledge Graph     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Canonical Resolution│
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Enrichment Agent   │
                    │      Gemini         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence Validation │
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Product Intelligence│
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Final Product       │
                    │ Intelligence        │
                    └─────────────────────┘
````

---

# Tech Stack

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* httpx
* BeautifulSoup
* pypdf
* Tavily
* Google Gemini
* python-dotenv
* python-multipart

---

# Project Structure

```text
backend/
│
├── app/
│   ├── agents/
│   │   ├── intake_agent.py
│   │   ├── research_agent.py
│   │   ├── source_validation_agent.py
│   │   ├── document_agent.py
│   │   ├── specification_agent.py
│   │   ├── conflict_agent.py
│   │   ├── akgp_agent.py
│   │   ├── canonical_resolution_agent.py
│   │   ├── enrichment_agent.py
│   │   ├── evidence_validation_agent.py
│   │   └── product_intelligence_agent.py
│   │
│   ├── dfoo/
│   │   ├── orchestrator.py
│   │   ├── task_repository.py
│   │   └── task_state.py
│   │
│   ├── knowledge/
│   │   ├── entities.py
│   │   └── graph.py
│   │
│   ├── schemas/
│   │   └── api.py
│   │
│   ├── services/
│   │   ├── source_discovery.py
│   │   ├── source_filter.py
│   │   └── product_image_extractor.py
│   │
│   └── main.py
│
├── .env
├── requirements.txt
├── README.md
└── venv/
```

---

# Requirements

Python 3.11 or later is recommended.

Check your Python version:

```bash
python --version
```

Expected:

```text
Python 3.11.x
```

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd product-intelligence/backend
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` has not been generated yet:

```bash
pip install fastapi uvicorn httpx pypdf beautifulsoup4 python-dotenv tavily-python google-genai
```

Then optionally freeze the environment:

```bash
pip freeze > requirements.txt
```

---

# Environment Variables

Create a `.env` file inside the `backend` directory.

```env
TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
```

The application loads these variables using `python-dotenv`.

Do **not** commit `.env` to Git.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# Running the Backend

From the `backend` directory with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

You should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI specification

```text
http://127.0.0.1:8000/openapi.json
```

Swagger UI can be used to run the complete investigation without needing Postman or curl.

---

# API Endpoints

## 1. Health Check

### `GET /`

Checks whether the backend is running.

### Example

```bash
curl http://127.0.0.1:8000/
```

### Response

```json
{
  "message": "Industrial Product Intelligence API is running"
}
```

---

# 2. Create Investigation

### `POST /investigate`

Starts a product intelligence investigation.

The investigation is given a manufacturer and MPN/product identifier.

### Request

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20"
}
```

### curl

```bash
curl -X POST \
  http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20"
  }'
```

### Response

```json
{
  "investigation_id": "1451993c-4d9a-42cc-94a6-d9e444d1d731",
  "status": "done"
}
```

The returned `investigation_id` is used to retrieve the investigation and final product intelligence.

---

# 3. Get Investigation

### `GET /investigate/{investigation_id}`

Returns the complete investigation.

This includes:

* Investigation status
* Original input
* Agent tasks
* Task status
* Task attempts
* Dependencies
* Agent outputs
* Final product intelligence

### Example

```bash
curl \
  http://127.0.0.1:8000/investigate/1451993c-4d9a-42cc-94a6-d9e444d1d731
```

### Response structure

```json
{
  "investigation_id": "...",
  "status": "done",
  "input": {
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20"
  },
  "result": {
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20",
    "product_category": "industrial_electrical",
    "enrichment": {},
    "family_specifications": {},
    "variants": [],
    "knowledge_graph": {},
    "conflict_resolutions": [],
    "quality": {},
    "commerce_readiness": {}
  },
  "tasks": []
}
```

---

# 4. Get Clean Product Intelligence

### `GET /investigate/{investigation_id}/result`

Returns only the final product intelligence.

This is the recommended endpoint for the frontend.

### Example

```bash
curl \
  http://127.0.0.1:8000/investigate/1451993c-4d9a-42cc-94a6-d9e444d1d731/result
```

### Response

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20",
  "product_category": "industrial_electrical",
  "enrichment": {
    "title": "...",
    "short_description": "...",
    "features": [],
    "applications": [],
    "search_keywords": [],
    "technical_summary": {},
    "variant_descriptions": []
  },
  "family_specifications": {},
  "variants": [],
  "knowledge_graph": {},
  "conflict_resolutions": [],
  "quality": {},
  "commerce_readiness": {
    "status": "ready"
  },
  "sources": []
}
```

---

# 5. List Investigations

### `GET /investigations`

Returns the investigation archive for the frontend history page.

Optional query parameter: `?q=search_term` filters by manufacturer, MPN, or category.

### Example

```bash
curl http://127.0.0.1:8000/investigations
```

### Response

```json
{
  "investigations": [
    {
      "investigation_id": "1451993c-4d9a-42cc-94a6-d9e444d1d731",
      "status": "done",
      "manufacturer": "Schneider Electric",
      "mpn": "iC60N C20",
      "product_category": "industrial_electrical",
      "source_count": 4,
      "variant_count": 3,
      "commerce_readiness": "ready",
      "created_at": "2026-08-12T08:30:00"
    }
  ]
}
```

Investigations are stored in memory for the current server session.

---

# 6. Extract Product From Image

### `POST /investigate/extract-from-image`

Uses Gemini 2.5 Flash to read a product/nameplate image and extract manufacturer and MPN before starting an investigation.

### Request

`multipart/form-data` with field `file`.

Supported types: JPEG, PNG, WebP, GIF (max 10 MB).

Requires `GEMINI_API_KEY` in `.env`.

### Example

```bash
curl -X POST \
  http://127.0.0.1:8000/investigate/extract-from-image \
  -F "file=@/path/to/product.jpg"
```

### Response

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "A9F77120",
  "notes": "Read from product label"
}
```

The frontend pre-fills the investigation form with this response, then calls `POST /investigate` as usual.

---

# Recommended Frontend Flow

The frontend should follow this sequence:

```text
Option A — Manual input
1. User enters manufacturer + MPN
              │
              ▼
2. POST /investigate
              │
              ▼
3. Poll GET /investigate/{id} until status is done
              │
              ▼
4. GET /investigate/{id}/result
              │
              ▼
5. Display final product intelligence

Option B — Image upload
1. User uploads product image
              │
              ▼
2. POST /investigate/extract-from-image
              │
              ▼
3. User reviews extracted manufacturer + MPN
              │
              ▼
4. Continue with Option A from step 2

History
1. GET /investigations
              │
              ▼
2. User selects a completed investigation
              │
              ▼
3. GET /investigate/{id}/result
```

For the final product page, use:

```text
GET /investigate/{id}/result
```

For showing the investigation pipeline/progress, use:

```text
GET /investigate/{id}
```

---

# Product Intelligence Response

The final response contains several major sections.

## Product information

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20",
  "product_category": "industrial_electrical"
}
```

---

## Enrichment

Commerce-oriented content generated from verified product intelligence.

```json
{
  "enrichment": {
    "title": "...",
    "short_description": "...",
    "features": [],
    "applications": [],
    "search_keywords": [],
    "technical_summary": {},
    "variant_descriptions": []
  }
}
```

---

## Family specifications

Specifications common to the product family.

Example:

```json
{
  "rated_current": {
    "value": "20",
    "unit": "A",
    "confidence": 0.8
  },
  "trip_curve": {
    "value": "C",
    "unit": null,
    "confidence": 0.8
  },
  "frequency": {
    "value": "50/60",
    "unit": "Hz",
    "confidence": 0.8
  }
}
```

---

## Variants

Variant-specific differences are kept separate from family-level specifications.

Example:

```json
{
  "mpn": "A9F77120",
  "specifications": {
    "poles": "1P"
  }
}
```

---

## Knowledge Graph

The AKGP stage generates a structured graph containing:

* Manufacturer
* Product family
* Product variants
* Relationships between them

Example:

```json
{
  "entities": [
    {
      "id": "manufacturer:Schneider Electric",
      "type": "Manufacturer"
    },
    {
      "id": "family:Schneider Electric:iC60N C20",
      "type": "ProductFamily"
    }
  ],
  "relationships": [
    {
      "source": "manufacturer:Schneider Electric",
      "type": "MANUFACTURES",
      "target": "family:Schneider Electric:iC60N C20"
    }
  ]
}
```

---

## Conflict Resolution

Conflicting specifications are analyzed rather than blindly merged.

Example:

```json
{
  "field": "poles",
  "status": "variant_difference",
  "requires_human_review": false
}
```

This allows the system to distinguish between:

```text
Actual contradiction
```

and:

```text
Different product variants
```

---

## Quality

The final quality object indicates whether human review is required.

```json
{
  "human_review_required": false,
  "unresolved_conflicts": []
}
```

---

## Commerce Readiness

Indicates whether the generated product record is ready for downstream commerce use.

```json
{
  "status": "ready"
}
```

Possible statuses include:

```text
ready
review_required
```

---

# Error Responses

## 404 — Investigation Not Found

Returned when an invalid investigation ID is provided.

```json
{
  "detail": "Investigation not found"
}
```

---

## 404 — Result Not Available

Returned when an investigation exists but its final result has not been generated.

```json
{
  "detail": "Investigation result not available"
}
```

---

## 404 — Product Intelligence Not Available

Returned when the investigation exists but does not contain a final product intelligence object.

```json
{
  "detail": "Product intelligence not available"
}
```

---

## 422 — Validation Error

Returned when the request body does not match the expected API schema.

Example:

```json
{
  "detail": [
    {
      "loc": ["body", "manufacturer"],
      "msg": "Field required"
    }
  ]
}
```

---

# Agent Pipeline

The investigation is orchestrated through DFOO.

The major stages are:

### 1. Intake Agent

Normalizes the initial product request.

### 2. Research Agent

Discovers external sources for the requested product.

### 3. Source Validation Agent

Validates and filters discovered sources.

### 4. Document Agent

Fetches source content and extracts usable text from HTML/PDF documents.

### 5. Specification Agent

Extracts structured technical specifications such as:

* Rated current
* Poles
* Trip curve
* Frequency
* Breaking capacity

### 6. Conflict Agent

Detects conflicting values across sources.

### 7. AKGP Agent

Builds the Attribute/Knowledge Graph representation of the product and its variants.

### 8. Canonical Resolution Agent

Separates:

* Family-level specifications
* Variant-level specifications
* Unresolved conflicts

### 9. Enrichment Agent

Uses Gemini to generate commerce-oriented content from the verified product intelligence.

### 10. Evidence Validation Agent

Checks generated/enriched information against available evidence.

### 11. Product Intelligence Agent

Combines all validated information into the final structured product intelligence response.

---

# Running a Test Investigation

Start the server:

```bash
python -m uvicorn app.main:app --reload
```

Then:

```bash
curl -X POST \
  http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20"
  }'
```

Copy the returned:

```text
investigation_id
```

Then:

```bash
curl \
  http://127.0.0.1:8000/investigate/<INVESTIGATION_ID>
```

Finally:

```bash
curl \
  http://127.0.0.1:8000/investigate/<INVESTIGATION_ID>/result
```

---

# Development

Run with hot reload:

```bash
python -m uvicorn app.main:app --reload
```

Run without reload:

```bash
python -m uvicorn app.main:app
```

---

# Notes

* External websites may reject automated requests with HTTP `403` responses. The research pipeline can continue using other discovered evidence sources.
* Product variants are kept separate from family-level specifications.
* Technical specifications should only be generated from available evidence.
* The final enrichment stage is instructed not to invent technical specifications.
* Investigation and task state are currently maintained by the backend repositories.
* The `/result` endpoint is intended to provide the frontend with the cleanest final product representation.

---

# API Summary

| Method | Endpoint                            | Purpose                              |
| ------ | ----------------------------------- | ------------------------------------ |
| `GET`  | `/`                                 | Backend health check                 |
| `POST` | `/investigate`                      | Start a product investigation        |
| `POST` | `/investigate/extract-from-image`   | Extract manufacturer/MPN from image  |
| `GET`  | `/investigations`                   | List investigation archive           |
| `GET`  | `/investigate/{id}`                 | Get complete investigation + tasks   |
| `GET`  | `/investigate/{id}/result`          | Get clean final product intelligence |
| `GET`  | `/docs`                             | Swagger API documentation            |
| `GET`  | `/redoc`                            | ReDoc API documentation              |
| `GET`  | `/openapi.json`                     | OpenAPI specification                |

---

# Quick Start

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

and run:

```text
POST /investigate
```

with:

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20"
}
```

The backend will execute the complete product intelligence pipeline and expose the final result through:

```text
GET /investigate/{investigation_id}/result
```

---

## Status

**Backend MVP: Complete**

The backend currently supports:

* Multi-agent product investigation
* External source discovery (Tavily)
* Source validation
* Document extraction
* Technical specification extraction
* Conflict detection
* Variant identification
* Knowledge graph construction
* Canonical product resolution
* LLM-based commerce enrichment (Gemini)
* Evidence validation
* Gemini image-based product identification
* Investigation archive listing
* Source metadata in final API responses
* Structured Pydantic API responses
* In-memory investigation/task tracking
* Swagger/OpenAPI documentation
