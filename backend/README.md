# Industrial Product Intelligence — Backend

AI-powered backend for researching, validating, resolving, and enriching industrial products.

The system accepts a manufacturer and manufacturer part number (MPN), runs a multi-agent investigation pipeline, and produces structured, commerce-ready product intelligence.

---

## Architecture

```text
Product Input
     |
     v
Intake Agent
     |
     v
Research Agent
     |
     v
Source Validation Agent
     |
     v
Document Agent
     |
     v
Specification Agent
     |
     v
Conflict Resolution
     |
     v
AKGP Agent
     |
     v
Canonical Resolution
     |
     v
Enrichment Agent
     |
     v
Evidence Validation
     |
     v
Product Intelligence