import {
  ArrowLeft,
  ChevronRight,
  Search,
} from "lucide-react";
import {
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import { listInvestigations } from "../services/api";
import type { InvestigationSummary } from "../types/api";

function formatCategory(
  value?: string | null
): string {
  if (!value) {
    return "Product investigation";
  }

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}

function formatStatusLabel(
  investigation: InvestigationSummary
): string {
  if (investigation.status === "done") {
    if (
      investigation.commerce_readiness ===
      "review_required"
    ) {
      return "Review required";
    }

    return "Ready";
  }

  if (investigation.status === "running") {
    return "Running";
  }

  if (investigation.status === "failed") {
    return "Failed";
  }

  return investigation.status;
}

function formatDate(
  value: string
): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function History() {
  const navigate = useNavigate();

  const [investigations, setInvestigations] =
    useState<InvestigationSummary[]>([]);

  const [searchQuery, setSearchQuery] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchInvestigations() {
      try {
        setLoading(true);
        setError(null);

        const response =
          await listInvestigations();

        if (!cancelled) {
          setInvestigations(
            response.investigations
          );
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load investigation history."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchInvestigations();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredInvestigations =
    useMemo(() => {
      const query =
        searchQuery.trim().toLowerCase();

      if (!query) {
        return investigations;
      }

      return investigations.filter(
        (investigation) => {
          const haystack = [
            investigation.manufacturer,
            investigation.mpn,
            investigation.product_category,
          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

          return haystack.includes(query);
        }
      );
    }, [investigations, searchQuery]);

  return (
    <main className="page-shell">
      <header className="page-header">
        <button
          className="back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={17} />
          Back
        </button>

        <div>
          <div className="eyebrow">
            INVESTIGATION ARCHIVE
          </div>

          <h1>Previous Investigations</h1>

          <p>
            Explore previously generated product
            intelligence.
          </p>
        </div>
      </header>

      <div className="search-bar">
        <Search size={18} />

        <input
          value={searchQuery}
          onChange={(event) =>
            setSearchQuery(
              event.target.value
            )
          }
          placeholder="Search manufacturer, MPN or product..."
        />
      </div>

      {error ? (
        <div className="error-banner">
          {error}
        </div>
      ) : null}

      <section className="history-list">
        {loading ? (
          <div className="history-empty">
            Loading investigations...
          </div>
        ) : filteredInvestigations.length ? (
          filteredInvestigations.map(
            (investigation) => (
              <InvestigationCard
                key={
                  investigation.investigation_id
                }
                investigation={investigation}
                onClick={() => {
                  if (
                    investigation.status !==
                    "done"
                  ) {
                    return;
                  }

                  navigate(
                    `/investigate/${investigation.investigation_id}`
                  );
                }}
              />
            )
          )
        ) : (
          <div className="history-empty">
            {searchQuery.trim()
              ? "No investigations match your search."
              : "No investigations yet. Start one from the home page."}
          </div>
        )}
      </section>
    </main>
  );
}

function InvestigationCard({
  investigation,
  onClick,
}: {
  investigation: InvestigationSummary;
  onClick: () => void;
}) {
  const isClickable =
    investigation.status === "done";

  return (
    <button
      className={`investigation-card${
        isClickable
          ? ""
          : " investigation-card--static"
      }`}
      onClick={onClick}
      disabled={!isClickable}
      type="button"
    >
      <div className="investigation-main">
        <div
          className={`status-dot status-dot--${investigation.status}`}
        />

        <div>
          <div className="card-manufacturer">
            {investigation.manufacturer ||
              "Unknown manufacturer"}
          </div>

          <div className="card-product mono">
            {investigation.mpn ||
              "Unknown product"}
          </div>

          <div className="card-meta">
            {formatCategory(
              investigation.product_category
            )}
            {investigation.created_at
              ? ` · ${formatDate(
                  investigation.created_at
                )}`
              : ""}
          </div>
        </div>
      </div>

      <div className="investigation-stats">
        <span>
          {investigation.source_count}{" "}
          source
          {investigation.source_count === 1
            ? ""
            : "s"}
        </span>
        <span>
          {investigation.variant_count}{" "}
          variant
          {investigation.variant_count === 1
            ? ""
            : "s"}
        </span>
        <span>
          {formatStatusLabel(investigation)}
        </span>
      </div>

      {isClickable ? (
        <ChevronRight size={19} />
      ) : null}
    </button>
  );
}

export default History;
