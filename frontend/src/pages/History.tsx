import { ArrowLeft, Search, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

function History() {
  const navigate = useNavigate();

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
          <div className="eyebrow">INVESTIGATION ARCHIVE</div>

          <h1>Previous Investigations</h1>

          <p>
            Explore previously generated product intelligence.
          </p>
        </div>
      </header>

      <div className="search-bar">
        <Search size={18} />

        <input
          placeholder="Search manufacturer, MPN or product..."
        />
      </div>

      <section className="history-list">
        <InvestigationCard
          manufacturer="Schneider Electric"
          product="iC60N C20"
          category="Industrial Electrical"
          sources={4}
          variants={3}
          onClick={() =>
            navigate(
              "/investigate/1451993c-4d9a-42cc-94a6-d9e444d1d731"
            )
          }
        />
      </section>
    </main>
  );
}

function InvestigationCard({
  manufacturer,
  product,
  category,
  sources,
  variants,
  onClick,
}: {
  manufacturer: string;
  product: string;
  category: string;
  sources: number;
  variants: number;
  onClick: () => void;
}) {
  return (
    <button className="investigation-card" onClick={onClick}>
      <div className="investigation-main">
        <div className="status-dot" />

        <div>
          <div className="card-manufacturer">
            {manufacturer}
          </div>

          <div className="card-product mono">
            {product}
          </div>

          <div className="card-meta">
            {category}
          </div>
        </div>
      </div>

      <div className="investigation-stats">
        <span>{sources} sources</span>
        <span>{variants} variants</span>
        <span>Ready</span>
      </div>

      <ChevronRight size={19} />
    </button>
  );
}

export default History;