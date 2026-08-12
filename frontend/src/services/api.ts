import type {
  InvestigationCreatedResponse,
  InvestigationRequest,
  InvestigationResponse,
  ProductIntelligence,
} from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      ...options,
    }
  );

  if (!response.ok) {
    let message = `API request failed: ${response.status}`;

    try {
      const error = await response.json();

      if (error?.detail) {
        message =
          typeof error.detail === "string"
            ? error.detail
            : JSON.stringify(error.detail);
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function createInvestigation(
  product: InvestigationRequest
): Promise<InvestigationCreatedResponse> {
  return request<InvestigationCreatedResponse>(
    "/investigate",
    {
      method: "POST",
      body: JSON.stringify(product),
    }
  );
}

export async function getInvestigation(
  investigationId: string
): Promise<InvestigationResponse> {
  return request<InvestigationResponse>(
    `/investigate/${investigationId}`
  );
}

export async function getInvestigationResult(
  investigationId: string
): Promise<ProductIntelligence> {
  return request<ProductIntelligence>(
    `/investigate/${investigationId}/result`
  );
}