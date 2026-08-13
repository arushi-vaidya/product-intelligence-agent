
# Industrial Product Intelligence — Frontend

> A modern interactive React interface for investigating industrial products, monitoring the intelligence pipeline, exploring product intelligence, and visualizing the Attribute Knowledge Graph.

---

## Overview

The Industrial Product Intelligence frontend provides the user-facing interface for the product investigation platform.

It connects to the FastAPI backend and turns the backend's structured product intelligence into an interactive investigation experience.

The frontend is designed around four primary workflows:

```text
┌─────────────────────┐
│     Landing Page    │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
New Investigation   Previous Investigations
     │           │
     ▼           ▼
Investigation     History
Pipeline             │
     │               │
     └───────┬───────┘
             ▼
       Results Page
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
   Product  Evidence  AKGP
 Intelligence         Graph
````

The interface focuses on making complex product intelligence understandable without exposing unnecessary backend complexity to the user.

---

# ✨ Features

## Product Investigation

Users can start an investigation by:

* Entering **Manufacturer** and **MPN** manually, or
* Uploading a **product image** — Gemini extracts manufacturer and product from the label/nameplate

Example manual input:

```text
Manufacturer:
Schneider Electric

MPN:
iC60N C20
```

Image flow:

```text
Upload image → Extract with Gemini → Review fields → Begin Investigation
```

The frontend sends the request to the backend and receives an investigation ID. The investigation page polls task progress until completion, then navigates to results.

---

## Investigation Pipeline

The investigation workflow visually represents the backend intelligence pipeline.

```text
Input
  ↓
Research
  ↓
Specification Extraction
  ↓
Conflict Resolution
  ↓
Canonical Resolution
  ↓
Enrichment
  ↓
Knowledge Graph
  ↓
Product Intelligence
```

This allows users to understand that the result is produced through multiple stages rather than a single opaque AI response.

---

# 📊 Results Dashboard

The results page presents the final product intelligence in structured sections.

### Product Overview

Displays:

* Product title
* Manufacturer
* MPN
* Product category
* Commerce readiness
* Average confidence

### Product Enrichment

Displays:

* Product description
* Features with linked source citations
* Applications with linked source citations
* Search keywords
* Sidebar sources with external links

### Technical Specifications

Displays:

* Family-level specifications
* Values, units, confidence scores, quality status
* Clickable source links from specification evidence

### Product Variants

Displays:

* Variant MPNs
* Variant-specific specifications
* Linked source tags per variant

### Evidence Resolution

Displays:

* Conflicting fields
* Resolution status
* Variant-specific values
* Human-review requirements

### Attribute Knowledge Graph

Provides an interactive representation of product relationships.

---

# 🧠 Attribute Knowledge Graph

The frontend includes an interactive AKGP visualization.

The graph represents relationships such as:

```text
Manufacturer
      │
      │ MANUFACTURES
      ▼
Product Family
      │
      ├── HAS_VARIANT ──► Variant A
      │
      ├── HAS_VARIANT ──► Variant B
      │
      └── HAS_VARIANT ──► Variant C
```

The graph UI supports:

* Zoom in
* Zoom out
* Reset zoom
* Entity selection
* Entity inspection
* Relationship inspection
* Variant exploration
* Entity property inspection

Selecting a graph node opens an inspector containing the node's properties and connected relationships.

---

# 🏗️ Frontend Architecture

The frontend follows a page/component structure.

```text
React Application
│
├── Pages
│   ├── Home
│   ├── New Investigation
│   ├── Results
│   └── History
│
├── Components
│   ├── Graph
│   │   └── AKGPGraph
│   └── SourceLink
│
├── Services
│   └── api.ts
│
├── API Integration
│   └── FastAPI Backend
│
└── Styling
    ├── Page CSS
    └── Component CSS
```

---

# 🗂️ Project Structure

A typical frontend structure:

```text
frontend/
│
├── public/
│
├── src/
│   │
│   ├── components/
│   │   │
│   │   └── Graph/
│   │       ├── AKGPGraph.tsx
│   │       └── AKGPGraph.css
│   │
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── NewInvestigation.tsx
│   │   ├── Results.tsx
│   │   ├── History.tsx
│   │   └── Results.css
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── .env
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

> The exact structure can differ depending on the current implementation.

---

# 🛠️ Tech Stack

## Core

* React
* TypeScript
* Vite

## Routing

* React Router

## Styling

* CSS
* Responsive layouts
* CSS animations
* Glass / dark UI styling

## Backend Communication

* REST API
* Fetch API

## Backend

The frontend communicates with:

```text
FastAPI
```

through the backend REST API.

---

# 🚀 Getting Started

## Prerequisites

Install:

* Node.js 18+
* npm

Verify:

```bash
node --version
npm --version
```

---

# 📦 Installation

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

# 🔐 Environment Variables

Create a `.env` file inside the frontend directory:

```text
frontend/.env
```

Add:

```env
VITE_API_URL=http://127.0.0.1:8000
```

See `frontend/.env.example`. The shared base URL lives in `src/config/api.ts`.

---

# 🚀 Deployment (Vercel)

1. Import the GitHub repo in [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Add environment variable:
   ```env
   VITE_API_URL=https://your-service.onrender.com
   ```
4. Deploy. SPA routing is configured in `vercel.json`.

```bash
cd frontend
vercel --prod
```

After deploy, set `FRONTEND_URL` on the Render backend to your Vercel URL.

---

# ▶️ Running the Frontend

Start the Vite development server:

```bash
npm run dev
```

The frontend will typically be available at:

```text
http://localhost:5173
```

---

# 🔗 Backend Requirement

The frontend requires the FastAPI backend to be running.

Start the backend separately:

```bash
cd backend

uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Frontend:

```text
http://localhost:5173
```

The two applications communicate through the REST API.

---

# 🔄 Application Flow

## 1. Landing Page

The user enters the application and can choose between:

```text
New Investigation
```

or:

```text
Previous Investigations
```

---

## 2. New Investigation

The user enters:

```text
Manufacturer
MPN
```

Example:

```text
Manufacturer: Siemens
MPN: 5SY4106-7
```

The frontend sends:

```http
POST /investigate
```

with:

```json
{
  "manufacturer": "Siemens",
  "mpn": "5SY4106-7"
}
```

The backend returns:

```json
{
  "investigation_id": "uuid",
  "status": "pending"
}
```

The frontend uses the investigation ID to track the investigation.

---

# ⏳ Investigation Processing

While the backend is processing the product, the frontend can display the investigation pipeline.

Example:

```text
✓ Research
│
✓ Specification Extraction
│
◌ Conflict Resolution
│
○ Canonical Resolution
│
○ Enrichment
│
○ Knowledge Graph
│
○ Product Intelligence
```

Task states are represented as:

```text
pending
running
done
retry
failed
```

---

# 📈 Results

Once the investigation is complete, the frontend loads:

```http
GET /investigate/{investigation_id}/result
```

The result is then transformed into the Results dashboard.

The page is organized into:

```text
Product Overview
       ↓
Product Enrichment
       ↓
Technical Specifications
       ↓
Product Variants
       ↓
Variant Intelligence
       ↓
Evidence Resolution
       ↓
Search Intelligence
       ↓
Attribute Knowledge Graph
       ↓
Commerce Readiness
```

---

# 🧾 Data Normalization

The backend's enrichment data may contain different JSON types.

For example:

```json
{
  "features": [
    "Feature A",
    "Feature B"
  ]
}
```

or:

```json
{
  "technical_summary": {
    "rated_current": "20 A",
    "frequency": "50/60 Hz"
  }
}
```

The frontend normalizes these values before rendering them.

This is important because React cannot directly render arbitrary JavaScript objects as JSX children.

For example:

```typescript
function displayValue(
  value: unknown
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value
      .map(displayValue)
      .join(", ");
  }

  if (typeof value === "object") {
    return Object.entries(value)
      .map(
        ([key, value]) =>
          `${key}: ${displayValue(value)}`
      )
      .join(" · ");
  }

  return String(value);
}
```

This keeps the UI resilient to structured LLM output.

---

# 🧭 Routes

The frontend uses React Router.

Recommended routes:

| Route                              | Purpose                 |
| ---------------------------------- | ----------------------- |
| `/`                                | Landing page            |
| `/investigate`                     | New investigation       |
| `/investigate/:investigationId`    | Investigation results   |
| `/history`                         | Previous investigations |

Example:

```tsx
<Routes>

  <Route
    path="/"
    element={<Home />}
  />

  <Route
    path="/investigate"
    element={<NewInvestigation />}
  />

  <Route
    path="/investigate/:investigationId"
    element={<Results />}
  />

  <Route
    path="/history"
    element={<History />}
  />

</Routes>
```

---

# 🔌 API Integration

The frontend communicates with the backend through `frontend/src/services/api.ts`:

| Function | Endpoint | Purpose |
| -------- | -------- | ------- |
| `createInvestigation` | `POST /investigate` | Start pipeline |
| `getInvestigation` | `GET /investigate/{id}` | Poll tasks and status |
| `getInvestigationResult` | `GET /investigate/{id}/result` | Load results page |
| `listInvestigations` | `GET /investigations` | History archive |
| `extractProductFromImage` | `POST /investigate/extract-from-image` | Gemini image extraction |

Example:

```typescript
const data = await getInvestigationResult(investigationId);
```

The backend API is responsible for investigation processing.

The frontend is responsible for:

* User interaction
* Navigation
* Loading states
* Error states
* Visualization
* Data presentation

---

# 🎨 UI Design

The interface uses a modern dark visual language designed for an industrial intelligence / developer-tool environment.

Major design characteristics:

* Dark background
* High-contrast typography
* Minimal visual noise
* Green intelligence/status accent
* Purple variant accent
* Blue manufacturer accent
* Rounded cards
* Subtle borders
* Soft gradients
* Interactive hover states
* Responsive layouts

---

# 🧩 Component Design

The frontend separates reusable visual functionality from pages.

For example:

```text
Results.tsx
      │
      ├── Product sections
      │
      ├── Specification cards
      │
      ├── Variant cards
      │
      └── AKGPGraph
              │
              ├── Graph canvas
              ├── Nodes
              ├── Relationships
              ├── Controls
              ├── Legend
              └── Entity Inspector
```

This keeps complex visualization logic out of the main Results page.

---

# 🔬 AKGP Component

The graph component receives only structured graph data:

```typescript
<AKGPGraph
  entities={knowledgeGraph.entities}
  relationships={
    knowledgeGraph.relationships
  }
/>
```

Entity format:

```typescript
type Entity = {
  id: string;
  type: string;
  properties?: Record<
    string,
    unknown
  >;
};
```

Relationship format:

```typescript
type Relationship = {
  source: string;
  type: string;
  target: string;
  properties?: Record<
    string,
    unknown
  >;
};
```

This makes the component independent of the backend implementation.

---

# 📱 Responsive Design

The frontend is designed to work across:

* Desktop
* Laptop
* Tablet
* Smaller screens

The AKGP visualization adapts its layout on smaller screens by switching from a horizontal graph arrangement to a stacked representation.

---

# ⚠️ Error Handling

The frontend handles several failure states.

### Backend unavailable

Displays an error state rather than leaving the page blank.

### Investigation not found

Displays:

```text
Investigation not found
```

### Result unavailable

Displays:

```text
Investigation result not available
```

### Missing investigation ID

Displays an appropriate error state.

### Empty knowledge graph

Displays an empty-state component instead of failing to render.

---

# 🐛 Common Development Issues

## CORS Error

If the browser reports a CORS error, verify that the backend allows:

```text
http://localhost:5173
```

and:

```text
http://127.0.0.1:5173
```

---

## API 404

Check:

```text
VITE_API_URL
```

and verify that the backend is running.

Expected:

```text
http://127.0.0.1:8000
```

---

## React Router: No routes matched

If the browser reports:

```text
No routes matched location "/investigate"
```

ensure `App.tsx` contains:

```tsx
<Route
  path="/investigate"
  element={<NewInvestigation />}
/>
```

---

## Results Page is Blank

Check the browser console and verify that:

```http
GET /investigate/{id}/result
```

returns a successful response.

Also verify that the frontend receives:

```json
{
  "product_intelligence": {}
}
```

or the clean product intelligence object expected by the frontend API contract.

---

## React Hook Order Error

Do not place hooks after conditional returns.

Incorrect:

```tsx
if (loading) {
  return <Loading />;
}

const data = useMemo(...);
```

Correct:

```tsx
const data = useMemo(...);

if (loading) {
  return <Loading />;
}
```

All hooks must be called in the same order on every render.

---

# 🧪 Testing a Product

A good test product is:

```text
Manufacturer:
Schneider Electric

MPN:
iC60N C20
```

Another useful test:

```text
Manufacturer:
Siemens

MPN:
5SY4106-7
```

The second query helps verify that the frontend isn't hardcoded to the Schneider Electric example.

---

# 🏃 Development Workflow

Run both applications in separate terminals.

### Terminal 1 — Backend

```bash
cd backend

source .venv/bin/activate

uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd frontend

npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# 📁 Frontend Environment

Development:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Production should use the deployed backend:

```env
VITE_API_URL=https://your-backend-domain.com
```

Never hardcode production URLs directly into components.

---

# 🔒 Security

The frontend should not contain private API credentials.

For example, the Gemini API key belongs on the backend:

```text
Backend
  ↓
GEMINI_API_KEY
```

and should never be exposed through:

```text
VITE_*
```

environment variables.

Vite variables prefixed with `VITE_` are bundled into the client and should therefore be treated as public.

---

# 🚀 Production Build

Create a production build:

```bash
npm run build
```

Preview it locally:

```bash
npm run preview
```

The generated production assets will be placed in:

```text
dist/
```

---

# 🧠 Frontend Responsibilities

The frontend intentionally does not perform product intelligence itself.

It does not:

* Search product sources
* Extract technical specifications
* Resolve product conflicts
* Decide canonical values
* Generate product descriptions
* Construct the knowledge graph

Those responsibilities belong to the backend.

The frontend instead provides the interface for:

```text
Input
  ↓
Investigation
  ↓
Visualization
  ↓
Inspection
  ↓
Decision
```

---

# 🔮 Future Improvements

Potential frontend improvements include:

### Investigation History

Additional history features:

* Sorting and date filters
* Persistent storage across server restarts (backend change)
* Pagination for large archives

### Evidence Explorer

Allow users to click a specification and view the original snippet inline.

### Human Review

Allow users to approve or override unresolved conflicts.

### Advanced AKGP

Expand the graph to include specifications, standards, applications, and related products.

### Export

Allow users to export product intelligence as JSON, CSV, or catalog format.

---

# 📋 Frontend Status

Current frontend capabilities:

* [x] React application
* [x] TypeScript
* [x] Vite development setup
* [x] React Router
* [x] Landing page
* [x] New investigation workflow
* [x] Backend API integration
* [x] Results dashboard
* [x] Product enrichment display
* [x] Technical specification display
* [x] Variant display
* [x] Conflict resolution display
* [x] Commerce readiness display
* [x] Interactive AKGP
* [x] Entity inspector
* [x] Graph zoom controls
* [x] Loading states
* [x] Error states
* [x] Responsive graph layout
* [x] Investigation history with search
* [x] Live task polling during investigations
* [x] Image upload and Gemini product extraction
* [x] Clickable source links on results

Planned:

* [ ] Evidence explorer (inline snippets)
* [ ] Human review UI
* [ ] Advanced graph relationships
* [ ] Export functionality

---

# 🏁 Summary

The Industrial Product Intelligence frontend provides a visual interface over the product intelligence pipeline.

Its primary purpose is to turn complex backend intelligence into an understandable workflow:

```text
┌──────────────────────┐
│ Product / MPN / Image│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Investigation     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Intelligence Pipeline│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Product Intelligence │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  Results       AKGP
     │           │
     └─────┬─────┘
           ▼
    Commerce-ready
     Intelligence
```

The frontend acts as the **interactive intelligence workspace**, allowing users to investigate products, understand how information was resolved, inspect variants and evidence, and explore the resulting product knowledge graph.
