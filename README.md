# Industrial Product Intelligence

> An AI-powered investigation and enrichment platform for transforming fragmented industrial product data into structured, canonical, commerce-ready product intelligence.

---

## Overview

Industrial product data is often scattered across manufacturer pages, technical documents, distributor listings, research snippets, and product variants.

The same product family may appear under different identifiers, contain incomplete specifications, or expose conflicting attributes across sources.

**Industrial Product Intelligence** solves this by building an automated investigation pipeline that:

1. Accepts a manufacturer and product identifier (MPN).
2. Investigates available product information.
3. Extracts technical specifications.
4. Collects and preserves supporting evidence.
5. Detects and resolves conflicting attributes.
6. Separates family-level specifications from variant-level differences.
7. Builds a canonical product representation.
8. Generates commerce-oriented product enrichment.
9. Constructs an Attribute Knowledge Graph (AKGP).
10. Produces a final product intelligence object that can be consumed by commerce, search, catalog, or downstream systems.

The project is designed around **evidence-backed product intelligence rather than simple text generation**.

---

# ✨ Key Features

## 🔎 Product Investigation

Start an investigation using:

- Manufacturer
- Manufacturer Part Number (MPN)
- **Product image upload** — Gemini reads the label/nameplate and extracts manufacturer + MPN before the pipeline runs

Example:

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20"
}
```

Or upload a photo on the investigation page; Gemini extracts the fields, you review them, then start the same pipeline.

---

## 🧠 Multi-stage Intelligence Pipeline

The backend processes products through multiple specialized agents:

```text
                    Product Input
                         │
                         ▼
                ┌─────────────────┐
                │ Research Agent  │
                └────────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Specification Agent  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Conflict Resolution  │
              └──────────┬───────────┘
                         │
                         ▼
             ┌────────────────────────┐
             │ Canonical Resolution   │
             └───────────┬────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Enrichment Agent│
                └────────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Knowledge Graph      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Product Intelligence │
              └──────────┬───────────┘
                         │
                         ▼
                 Commerce Ready
```

Each stage has a focused responsibility rather than relying on one large model call.

---

# 🏗️ Architecture

The project is divided into two major layers.

```text
┌────────────────────────────────────────────────────────────┐
│                        FRONTEND                            │
│                                                            │
│  Landing Page → Investigation → Processing → Results       │
│                       │                                    │
│                       └── Investigation History            │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           │ REST API
                           ▼
┌────────────────────────────────────────────────────────────┐
│                         BACKEND                            │
│                                                            │
│                       FastAPI                              │
│                          │                                 │
│                         DFOO                               │
│                          │                                 │
│          ┌───────────────┼───────────────┐                 │
│          ▼               ▼               ▼                 │
│      Agents          Repositories     Task State            │
│          │                                               │
│          ▼                                               │
│   Product Intelligence                                  │
└────────────────────────────────────────────────────────────┘
```

---

# 🧩 Backend

The backend is implemented using **FastAPI** and exposes REST endpoints for creating and retrieving investigations.

## Backend responsibilities

* API layer
* Investigation lifecycle
* Task orchestration
* Agent execution
* Specification extraction
* Conflict resolution
* Canonicalization
* Product enrichment
* Knowledge graph construction
* Product intelligence generation
* Task and investigation state management

---

# 🤖 Agents

The intelligence pipeline is composed of specialized agents.

## 1. Research Agent

Responsible for collecting product information from available sources.

The research stage produces evidence such as:

```json
{
  "source_id": "src_1",
  "title": "Product documentation",
  "url": "...",
  "snippet": "..."
}
```

The system preserves source information so downstream agents can reason over evidence.

---

## 2. Specification Agent

Extracts structured technical attributes from collected documents.

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
  },
  "breaking_capacity": {
    "value": "10",
    "unit": "kA",
    "confidence": 0.8
  }
}
```

The agent also preserves evidence for extracted values.

---

## 3. Conflict Resolution Agent

Product sources may disagree.

For example:

```text
Variant A → 1P
Variant B → 1P
Variant C → 2P
```

Instead of treating this as a global contradiction, the system determines whether the difference belongs to different product variants.

Example:

```json
{
  "field": "poles",
  "status": "variant_difference",
  "requires_human_review": false
}
```

This prevents incorrect family-level normalization.

---

## 4. Canonical Resolution Agent

The canonicalization stage produces a normalized representation of the product family.

It separates:

### Family-level specifications

```text
Rated current
Trip curve
Frequency
Breaking capacity
```

from:

### Variant-level specifications

```text
MPN
Poles
Variant-specific attributes
```

Example:

```json
{
  "family_specifications": {
    "rated_current": {
      "value": "20",
      "unit": "A",
      "confidence": 0.8
    }
  },
  "variants": [
    {
      "mpn": "A9F77120",
      "specifications": {
        "poles": "1P"
      }
    }
  ]
}
```

---

## 5. Enrichment Agent

The enrichment stage transforms verified product intelligence into commerce-oriented content.

It generates:

* Product title
* Short description
* Features
* Applications
* Search keywords
* Technical summary
* Variant descriptions

The enrichment agent is explicitly instructed not to invent technical specifications.

It receives:

```text
Canonical Product
+
Evidence
```

and generates structured JSON.

The project currently uses:

```text
Gemini 2.5 Flash
```

for this stage.

---

## 6. Knowledge Graph / AKGP

The system builds an **Attribute Knowledge Graph** representing relationships between:

* Manufacturers
* Product families
* Product variants

Example:

```text
Schneider Electric
        │
        │ MANUFACTURES
        ▼
     iC60N C20
        │
        ├──────── HAS_VARIANT ────────► A9F77120
        │
        ├──────── HAS_VARIANT ────────► A9F74120
        │
        └──────── HAS_VARIANT ────────► A9F74220
```

The graph is returned as entities and relationships.

Example entity:

```json
{
  "id": "manufacturer:Schneider Electric",
  "type": "Manufacturer",
  "properties": {
    "name": "Schneider Electric"
  }
}
```

Example relationship:

```json
{
  "source": "family:Schneider Electric:iC60N C20",
  "type": "HAS_VARIANT",
  "target": "variant:Schneider Electric:A9F77120"
}
```

The frontend provides an interactive graph explorer where users can:

* Zoom
* Inspect entities
* View relationships
* Inspect properties
* Explore product variants

---

## 7. Product Intelligence Agent

The final agent combines the outputs of the pipeline into a single product intelligence object.

The final object contains:

```text
manufacturer
mpn
product_category
enrichment
family_specifications
variants
knowledge_graph
conflict_resolutions
quality
commerce_readiness
```

---

# 📦 Final Product Intelligence

A simplified final response looks like:

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

  "knowledge_graph": {
    "entities": [],
    "relationships": []
  },

  "conflict_resolutions": [],

  "quality": {
    "human_review_required": false,
    "unresolved_conflicts": []
  },

  "commerce_readiness": {
    "status": "ready"
  }
}
```

---

# 🖥️ Frontend

The frontend is designed as a modern investigation workspace rather than a traditional CRUD interface.

## Main application flow

```text
Landing Page
     │
     ├───────────────► New Investigation
     │                       │
     │                       ▼
     │                  Investigation
     │                    Pipeline
     │                       │
     │                       ▼
     │                    Results
     │
     └───────────────► Previous Investigations
                             │
                             ▼
                         History
                             │
                             ▼
                           Results
```

---

# 🏠 Landing Page

The landing page acts as the entry point to the platform.

Primary actions:

### New Investigation

Starts a new product investigation.

### Previous Investigations

Opens the investigation history.

The landing page is intentionally focused on the two primary workflows.

---

# 🔍 New Investigation

The investigation page provides:

* Compact product image upload (drag & drop or browse)
* Gemini-based extraction of manufacturer and MPN from the image
* Manual manufacturer and MPN inputs
* Investigation start action
* Visual representation of the 11-stage intelligence pipeline

Example manual flow:

```text
Manufacturer
┌──────────────────────────────┐
│ Schneider Electric           │
└──────────────────────────────┘

MPN
┌──────────────────────────────┐
│ iC60N C20                    │
└──────────────────────────────┘

             [ Investigate ]
```

Or upload a product/nameplate image, click **Extract manufacturer & product**, review the filled fields, then begin the investigation.

The page then transitions into the live investigation pipeline view.

---

# ⚙️ Investigation Pipeline

The frontend represents the backend agent workflow visually.

Example:

```text
INPUT
  │
  ▼
Research
  │
  ▼
Specification Extraction
  │
  ▼
Conflict Resolution
  │
  ▼
Canonical Resolution
  │
  ▼
Enrichment
  │
  ▼
Knowledge Graph
  │
  ▼
Product Intelligence
  │
  ▼
READY
```

Tasks can expose states such as:

```text
Pending
Running
Done
Retry
Failed
```

---

# 📚 Investigation History

The history page lists previous investigations from the backend archive.

Each card displays:

* Manufacturer
* MPN / product identifier
* Product category (when available)
* Source and variant counts
* Status (Ready, Running, Failed, Review required)
* Creation timestamp

Features:

* Live fetch from `GET /investigations`
* Search by manufacturer, MPN, or category
* Click-through to results for completed investigations

**Note:** Investigations are stored in memory for the current backend session and reset when the server restarts.

---

# 📊 Results Page

The results page presents the complete product intelligence generated by the pipeline.

## Product Overview

Displays:

* Product title
* Manufacturer
* MPN
* Category
* Commerce readiness
* Confidence

---

## Product Enrichment

Displays:

* Short description
* Features with source citations (linked where available)
* Applications with source citations
* Search keywords
* Sidebar **Supported By** list with links to original sources

---

## Technical Specifications

Displays canonical family-level specifications with clickable source links from extracted evidence.

Example:

```text
Rated Current       20 A       80%
Trip Curve          C          80%
Frequency           50/60 Hz   80%
Breaking Capacity   10 kA      80%
```

---

## Product Variants

Displays variant-specific information separately from family-level specifications, including linked source tags per variant.

Example:

```text
A9F77120
1P

A9F74120
1P

A9F74220
2P
```

---

## Evidence Resolution

Displays how conflicting information was interpreted.

Example:

```text
Field: Poles

1P → A9F77120
1P → A9F74120
2P → A9F74220

Resolution:
Values belong to different product variants.

Human review:
Not required
```

---

## Attribute Knowledge Graph

The results page contains an interactive AKGP visualization.

Users can:

* Inspect nodes
* Inspect relationships
* Zoom
* Reset the graph
* Explore variants
* View entity properties

---

# 🔌 API

The backend exposes a REST API through FastAPI.

Base URL during local development:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

# API Endpoints

## GET /

Health check.

### Response

```json
{
  "message": "Industrial Product Intelligence API is running"
}
```

---

## POST /investigate

Creates and starts a product investigation.

### Request

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "iC60N C20"
}
```

### Response

```json
{
  "investigation_id": "uuid",
  "status": "done"
}
```

The investigation ID is then used to retrieve the investigation.

---

## POST /investigate/extract-from-image

Extracts manufacturer and MPN from an uploaded product image using Gemini 2.5 Flash.

### Request

`multipart/form-data` with a `file` field (JPEG, PNG, WebP, or GIF, max 10 MB).

### Response

```json
{
  "manufacturer": "Schneider Electric",
  "mpn": "A9F77120",
  "notes": "Read from product label"
}
```

The frontend uses this to pre-fill the investigation form before calling `POST /investigate`.

---

## GET /investigations

Returns the investigation archive for the history page.

Optional query parameter:

```text
?q=schneider
```

### Response

```json
{
  "investigations": [
    {
      "investigation_id": "uuid",
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

---

# GET /investigate/{investigation_id}

Returns the complete investigation state.

### Response structure

```json
{
  "investigation_id": "uuid",
  "status": "done",

  "input": {
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20"
  },

  "result": {},

  "tasks": []
}
```

Tasks expose information such as:

```text
agent
status
attempts
dependencies
output
```

---

# GET /investigate/{investigation_id}/result

Returns the clean final product intelligence object.

This endpoint is intended for the frontend and downstream consumers.

Example:

```text
GET /investigate/UUID/result
```

The response contains:

```text
Product Intelligence
├── Manufacturer
├── MPN
├── Category
├── Sources (id, url, title, authority tier)
├── Enrichment
├── Family Specifications (with evidence + source URLs)
├── Variants
├── Knowledge Graph
├── Conflict Resolutions
├── Evidence Validation
├── Quality
└── Commerce Readiness
```

---

# 🔄 Investigation State

The backend models investigation and task state explicitly.

Supported states:

```text
pending
running
done
retry
failed
```

This allows the frontend to represent investigation progress and enables task-level observability.

---

# 🗂️ Project Structure

A simplified repository structure:

```text
industrial-product-intelligence/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── research_agent.py
│   │   │   ├── specification_agent.py
│   │   │   ├── conflict_resolution_agent.py
│   │   │   ├── canonical_resolution_agent.py
│   │   │   ├── enrichment_agent.py
│   │   │   └── product_intelligence_agent.py
│   │   │
│   │   ├── dfoo/
│   │   │   └── orchestrator.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── investigation_repository.py
│   │   │   └── task_repository.py
│   │   │
│   │   ├── schemas/
│   │   │   └── api.py
│   │   │
│   │   └── main.py
│   │
│   ├── .env
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   │
│   ├── src/
│   │   │
│   │   ├── components/
│   │   │   └── Graph/
│   │   │       ├── AKGPGraph.tsx
│   │   │       └── AKGPGraph.css
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── NewInvestigation.tsx
│   │   │   ├── Results.tsx
│   │   │   └── History.tsx
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── .env
│   ├── package.json
│   └── README.md
│
└── README.md
```

> Exact filenames may differ depending on the implementation.

---

# 🚀 Getting Started

## Prerequisites

Install:

* Python 3.10+
* Node.js 18+
* npm
* Git

A Gemini API key is required for the enrichment stage.

---

# ⚙️ Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` to Git.

Add this to `.gitignore`:

```text
.env
.venv/
__pycache__/
```

---

# ▶️ Run the Backend

From the backend directory:

```bash
uvicorn app.main:app --reload
```

The API should now be available at:

```text
http://127.0.0.1:8000
```

Open the Swagger interface:

```text
http://127.0.0.1:8000/docs
```

---

# 🎨 Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
frontend/.env
```

Add:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will typically be available at:

```text
http://localhost:5173
```

---

# 🔗 Frontend ↔ Backend

The frontend communicates with the FastAPI backend through REST endpoints.

Example:

```text
Frontend
   │
   │ POST /investigate
   ▼
FastAPI
   │
   ▼
DFOO
   │
   ▼
Agent Pipeline
   │
   ▼
Investigation Repository
   │
   ▼
Frontend
   │
   │ GET /investigate/{id}/result
   ▼
Results Page
```

---

# 🌐 CORS

Local development origins are allowed by default. In production, configure:

```env
FRONTEND_URL=https://your-app.vercel.app
CORS_ORIGINS=https://custom-domain.com
```

All `*.vercel.app` preview deployments are allowed automatically via origin regex.

---

# 🚀 Deployment

## Backend — Render

The repo includes a [`render.yaml`](render.yaml) blueprint.

1. Push this repository to GitHub.
2. In [Render](https://render.com), click **New → Blueprint** and connect the repo.
3. Set secret environment variables when prompted:
   - `TAVILY_API_KEY`
   - `GEMINI_API_KEY`
   - `FRONTEND_URL` — your Vercel production URL (set after frontend deploy)
4. Deploy. Note the service URL, e.g. `https://product-intelligence-api.onrender.com`.

Manual setup (without Blueprint):

| Setting | Value |
| -------- | ----- |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check | `/` |

**Render free tier notes:** the service sleeps after inactivity (cold starts), and investigation history is in-memory (resets on redeploy/restart).

---

## Frontend — Vercel

1. In [Vercel](https://vercel.com), **Add New → Project** and import the GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Add environment variable:
   ```env
   VITE_API_URL=https://your-service.onrender.com
   ```
   (no trailing slash)
4. Deploy. Vercel uses `frontend/vercel.json` for SPA routing.

CLI deploy from the frontend folder:

```bash
cd frontend
vercel --prod
```

Set `VITE_API_URL` in the Vercel project settings before building.

---

## Post-deploy checklist

1. Deploy backend on Render → copy API URL.
2. Set `VITE_API_URL` on Vercel → redeploy frontend.
3. Set `FRONTEND_URL` on Render to your Vercel URL → redeploy backend (CORS).
4. Test: open Vercel app → start an investigation → confirm API calls succeed.

---

# 🧪 Example Investigation

Start the backend:

```bash
uvicorn app.main:app --reload
```

Then execute:

```bash
curl -X POST \
  http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Schneider Electric",
    "mpn": "iC60N C20"
  }'
```

Example response:

```json
{
  "investigation_id": "1451993c-4d9a-42cc-94a6-d9e444d1d731",
  "status": "done"
}
```

Retrieve the investigation:

```bash
curl \
  http://127.0.0.1:8000/investigate/1451993c-4d9a-42cc-94a6-d9e444d1d731
```

Or retrieve the clean result:

```bash
curl \
  http://127.0.0.1:8000/investigate/1451993c-4d9a-42cc-94a6-d9e444d1d731/result
```

---

# 📋 Example Output

For a Schneider Electric iC60N C20 investigation, the system can produce information such as:

```text
Manufacturer
Schneider Electric

MPN
iC60N C20

Product
Acti9 iC60N Miniature Circuit Breaker

Family Specifications
────────────────────────────────
Rated Current       20 A
Trip Curve          C
Frequency           50/60 Hz
Breaking Capacity   10 kA

Variants
────────────────────────────────
A9F77120             1P
A9F74120             1P
A9F74220             2P

Commerce Readiness
────────────────────────────────
READY
```

The resulting knowledge graph represents the manufacturer, family, and variants as connected entities.

---

# 🛡️ Data Quality Philosophy

A key design principle of the system is:

> **Do not turn uncertainty into false certainty.**

The pipeline therefore distinguishes between:

### Family-level information

Information that applies to the entire product family.

### Variant-level information

Information that differs between individual MPNs.

### Conflicting information

Information that cannot safely be reconciled automatically.

### Human review

Cases where automated resolution is insufficient.

This produces a more reliable catalog representation than simply asking an LLM to generate a product description.

---

# 🎯 Commerce Readiness

The final system evaluates whether a product can safely proceed to commerce-oriented usage.

Example:

```json
{
  "commerce_readiness": {
    "status": "ready"
  }
}
```

or:

```json
{
  "commerce_readiness": {
    "status": "review_required"
  }
}
```

A product requiring human review should not be treated as fully resolved.

---

# 🔬 Design Principles

## Evidence First

Product claims should originate from collected evidence or canonical product intelligence.

---

## Separation of Concerns

Each agent has a focused responsibility.

Research should not perform enrichment.

Enrichment should not redefine canonical specifications.

Canonicalization should not invent missing values.

---

## Variant Awareness

Differences between MPNs should not automatically be treated as contradictions.

---

## Structured Outputs

Agents communicate using structured data rather than unstructured prose.

---

## Explainability

The system preserves:

* Evidence
* Sources
* Confidence
* Conflict resolutions
* Relationships

so users can understand how the final product representation was produced.

---

# 🧠 Why an Agent Pipeline?

A single LLM call could produce a product description, but it would make it difficult to:

* Trace where specifications came from
* Handle conflicting sources
* Separate family and variant information
* Retry individual processing stages
* Inspect pipeline state
* Add new intelligence stages
* Support human review

The agent architecture makes each stage independently observable and replaceable.

---

# 🔮 Future Improvements

Potential extensions include:

### Better source verification

Add source reliability scoring and stronger manufacturer-source prioritization.

### Human review workflow

Allow users to approve or reject unresolved attributes directly from the UI.

### Persistent database

Move investigation/task storage to PostgreSQL or another production database.

### Background workers

Move long-running investigations into a proper asynchronous worker architecture.

### Advanced AKGP

Expand the graph beyond manufacturer → family → variant to include:

```text
Manufacturer
    │
    ├── Product Family
    │       │
    │       ├── Variant
    │       ├── Specification
    │       ├── Standard
    │       ├── Application
    │       └── Category
    │
    └── Brand
```

### Source-level visualization

Users can follow clickable source links from enrichment, specifications, and variants to the original URLs. Future work could add inline evidence snippets on the results page.

### Catalog integration

Expose product intelligence to:

* Search systems
* Product catalogs
* E-commerce platforms
* Recommendation systems
* PIM systems
* Procurement workflows

---


# 🏆 Example Use Cases

## Industrial Catalog Enrichment

Convert fragmented manufacturer information into structured product catalog data.

---

## Product Search

Generate normalized technical attributes and search keywords to improve product discovery.

---

## Procurement

Help procurement teams understand equivalent variants and technical differences.

---

## Product Information Management

Create canonical product families and variant structures for PIM systems.

---

## E-commerce

Generate commerce-ready titles, descriptions, features, applications, and technical summaries from verified information.

---

# 👥 Development

## Backend

```text
Python
FastAPI
Pydantic
Google Gemini
Tavily
DFOO
```

## Frontend

```text
React
TypeScript
Vite
React Router
CSS
```

---

# ⭐ Summary

Industrial Product Intelligence turns:

```text
Manufacturer + MPN  (or product image)
        │
        ▼
Fragmented product information
        │
        ▼
Evidence-backed investigation
        │
        ▼
Structured specifications
        │
        ▼
Conflict resolution
        │
        ▼
Canonical product family
        │
        ▼
Commerce enrichment
        │
        ▼
Attribute Knowledge Graph
        │
        ▼
Commerce-ready Product Intelligence
```

The goal is not simply to generate better product descriptions.

The goal is to build a **traceable, structured, variant-aware intelligence layer for industrial products** that downstream commerce and catalog systems can trust.

```
