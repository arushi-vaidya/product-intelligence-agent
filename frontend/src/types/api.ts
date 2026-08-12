// src/types/api.ts

// ==========================================
// GENERIC JSON TYPES
// ==========================================

export type JsonPrimitive =
  | string
  | number
  | boolean
  | null;

export type JsonValue =
  | JsonPrimitive
  | JsonValue[]
  | {
      [key: string]: JsonValue;
    };


// ==========================================
// INVESTIGATION
// ==========================================

export interface InvestigationRequest {
  manufacturer: string;
  mpn: string;
}

export interface InvestigationCreatedResponse {
  investigation_id: string;
  status: string;
}

export interface InvestigationSummary {
  investigation_id: string;
  status: string;
  manufacturer: string;
  mpn: string;
  product_category?: string | null;
  source_count: number;
  variant_count: number;
  commerce_readiness?: string | null;
  created_at: string;
}

export interface InvestigationListResponse {
  investigations: InvestigationSummary[];
}


// ==========================================
// SPECIFICATIONS
// ==========================================

export interface SpecificationEvidence {
  source_id?: string;
  source_url?: string | null;
  source_title?: string | null;
  value?: string | number | null;
  unit?: string | null;
  text?: string | null;
}

export interface Specification {
  value: string | number | null;
  unit?: string | null;
  confidence?: number | null;
  quality_status?: string | null;
  evidence?: SpecificationEvidence[];
}


// ==========================================
// SOURCES
// ==========================================

export interface ProductSource {
  id: string;
  url?: string | null;
  title?: string | null;
  source_type?: string | null;
  authority_tier?: number | null;
}


// ==========================================
// VARIANTS
// ==========================================

export interface ProductVariant {
  mpn: string;

  specifications:
    Record<string, string | number | boolean | null>;

  sources?: string[];
}


// ==========================================
// CONFLICTS
// ==========================================

export interface ConflictVariant {
  mpn: string;
  value: string | number | boolean | null;
}

export interface ConflictResolution {
  field: string;

  status: string;

  explanation?: string;

  variants?: ConflictVariant[];

  requires_human_review?: boolean;
}


// ==========================================
// KNOWLEDGE GRAPH
// ==========================================

export interface KnowledgeGraphEntity {
  id: string;
  type: string;

  properties?: Record<
    string,
    JsonValue
  >;
}

export interface KnowledgeGraphRelationship {
  source: string;
  type: string;
  target: string;

  properties?: Record<
    string,
    JsonValue
  >;
}

export interface KnowledgeGraph {
  entities?: KnowledgeGraphEntity[];

  relationships?: KnowledgeGraphRelationship[];
}


// ==========================================
// ENRICHMENT
// ==========================================

/**
 * Enrichment coming from the LLM can sometimes
 * contain strings, arrays, or structured objects.
 *
 * We therefore intentionally allow JsonValue here.
 */

export interface VariantDescription {
  mpn: string;

  description:
    | string
    | JsonValue;
}

export interface TechnicalSummary {
  [key: string]: JsonValue;
}

export interface ProductEnrichment {
  title?: string | JsonValue;

  short_description?:
    | string
    | JsonValue;

  features?: JsonValue;

  applications?: JsonValue;

  search_keywords?: JsonValue;

  technical_summary?:
    | TechnicalSummary
    | JsonValue;

  variant_descriptions?:
    | VariantDescription[]
    | JsonValue;
}


// ==========================================
// QUALITY
// ==========================================

export interface ProductQuality {
  human_review_required?: boolean;

  unresolved_conflicts?:
    ConflictResolution[];
}


// ==========================================
// COMMERCE READINESS
// ==========================================

export interface CommerceReadiness {
  status: string;
}


// ==========================================
// PRODUCT INTELLIGENCE
// ==========================================

export interface ProductIntelligence {
  manufacturer: string;

  mpn: string;

  product_category?: string;

  enrichment?: ProductEnrichment;

  family_specifications:
    Record<
      string,
      Specification
    >;

  variants: ProductVariant[];

  knowledge_graph?: KnowledgeGraph;

  conflict_resolutions:
    ConflictResolution[];

  quality: ProductQuality;

  commerce_readiness:
    CommerceReadiness;

  sources?: ProductSource[];
}


// ==========================================
// TASK
// ==========================================

export interface TaskResponse {
  id: string;

  agent: string;

  status: string;

  attempts: number;

  depends_on: string[];

  output?: JsonValue | null;
}


// ==========================================
// FULL INVESTIGATION RESPONSE
// ==========================================

export interface InvestigationResponse {
  investigation_id: string;

  status: string;

  input: InvestigationRequest;

  result?: ProductIntelligence | null;

  tasks: TaskResponse[];
}