import { useMemo, useState } from "react";
import "./AKGPGraph.css";

type Entity = {
  id: string;
  type: string;
  properties?: Record<string, unknown>;
};

type Relationship = {
  source: string;
  type: string;
  target: string;
  properties?: Record<string, unknown>;
};

type AKGPGraphProps = {
  entities: Entity[];
  relationships: Relationship[];
};

function displayValue(value: unknown): string {
  if (value === null || value === undefined) {
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
      .map((item) => displayValue(item))
      .join(", ");
  }

  if (typeof value === "object") {
    return Object.entries(
      value as Record<string, unknown>
    )
      .map(
        ([key, item]) =>
          `${formatFieldName(key)}: ${displayValue(item)}`
      )
      .join(" · ");
  }

  return String(value);
}

function formatFieldName(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getEntityName(entity: Entity): string {
  const name = entity.properties?.name;

  if (name !== undefined && name !== null) {
    return displayValue(name);
  }

  const mpn = entity.properties?.mpn;

  if (mpn !== undefined && mpn !== null) {
    return displayValue(mpn);
  }

  const parts = entity.id.split(":");

  return parts[parts.length - 1] || entity.id;
}

function shortId(id: string): string {
  const parts = id.split(":");
  return parts[parts.length - 1] || id;
}

export default function AKGPGraph({
  entities,
  relationships,
}: AKGPGraphProps) {
  const [selectedId, setSelectedId] =
    useState<string | null>(null);

  const [zoom, setZoom] = useState(1);

  const manufacturer = useMemo(
    () =>
      entities.find(
        (entity) => entity.type === "Manufacturer"
      ),
    [entities]
  );

  const family = useMemo(
    () =>
      entities.find(
        (entity) => entity.type === "ProductFamily"
      ),
    [entities]
  );

  const variants = useMemo(
    () =>
      entities.filter(
        (entity) => entity.type === "ProductVariant"
      ),
    [entities]
  );

  const selectedEntity = entities.find(
    (entity) => entity.id === selectedId
  );

  const selectedRelationships = selectedEntity
    ? relationships.filter(
        (relationship) =>
          relationship.source === selectedEntity.id ||
          relationship.target === selectedEntity.id
      )
    : [];

  const zoomIn = () => {
    setZoom((current) =>
      Math.min(current + 0.1, 1.5)
    );
  };

  const zoomOut = () => {
    setZoom((current) =>
      Math.max(current - 0.1, 0.7)
    );
  };

  const resetZoom = () => {
    setZoom(1);
  };

  if (!entities.length) {
    return (
      <div className="akgp-empty">
        <div className="akgp-empty-icon">◇</div>

        <strong>No knowledge graph available</strong>

        <span>
          The investigation did not return graph entities.
        </span>
      </div>
    );
  }

  return (
    <div className="akgp">

      {/* =====================================================
          TOOLBAR
          ===================================================== */}

      <div className="akgp-toolbar">

        <div className="akgp-stat-group">

          <div className="akgp-stat">
            <strong>{entities.length}</strong>
            <span>Entities</span>
          </div>

          <div className="akgp-stat">
            <strong>{relationships.length}</strong>
            <span>Relations</span>
          </div>

          <div className="akgp-stat">
            <strong>{variants.length}</strong>
            <span>Variants</span>
          </div>

        </div>

        <div className="akgp-controls">

          <button
            type="button"
            onClick={zoomOut}
            aria-label="Zoom out"
          >
            −
          </button>

          <span>
            {Math.round(zoom * 100)}%
          </span>

          <button
            type="button"
            onClick={zoomIn}
            aria-label="Zoom in"
          >
            +
          </button>

          <button
            type="button"
            className="akgp-reset"
            onClick={resetZoom}
          >
            Reset
          </button>

        </div>

      </div>


      {/* =====================================================
          GRAPH
          ===================================================== */}

      <div className="akgp-canvas">

        <div className="akgp-grid" />

        <div
          className="akgp-world"
          style={{
            transform: `scale(${zoom})`,
          }}
        >

          {/* ================================================
              MANUFACTURER
              ================================================ */}

          {manufacturer && (
            <button
              type="button"
              className={[
                "akgp-node",
                "manufacturer-node",
                selectedId === manufacturer.id
                  ? "selected"
                  : "",
              ].join(" ")}
              onClick={() =>
                setSelectedId(manufacturer.id)
              }
            >

              <div className="node-icon">
                ◉
              </div>

              <span className="node-type">
                MANUFACTURER
              </span>

              <strong>
                {getEntityName(manufacturer)}
              </strong>

              <small>
                {shortId(manufacturer.id)}
              </small>

            </button>
          )}


          {/* ================================================
              MANUFACTURER → FAMILY
              ================================================ */}

          {manufacturer && family && (
            <div className="akgp-horizontal-edge manufacturer-edge">

              <span className="edge-label">
                MANUFACTURES
              </span>

              <span className="edge-arrow">
                →
              </span>

            </div>
          )}


          {/* ================================================
              FAMILY
              ================================================ */}

          {family && (
            <button
              type="button"
              className={[
                "akgp-node",
                "family-node",
                selectedId === family.id
                  ? "selected"
                  : "",
              ].join(" ")}
              onClick={() =>
                setSelectedId(family.id)
              }
            >

              <div className="node-icon">
                ◆
              </div>

              <span className="node-type">
                PRODUCT FAMILY
              </span>

              <strong>
                {getEntityName(family)}
              </strong>

              <small>
                {shortId(family.id)}
              </small>

            </button>
          )}


          {/* ================================================
              FAMILY → VARIANTS
              ================================================ */}

          {family && variants.length > 0 && (
            <div className="akgp-vertical-edge">

              <span className="edge-label">
                HAS_VARIANT
              </span>

            </div>
          )}


          {/* ================================================
              VARIANTS
              ================================================ */}

          <div className="akgp-variants">

            {variants.map((variant) => {

              const specs =
                variant.properties
                  ?.specifications;

             const poles: string | undefined =
                specs &&
                typeof specs === "object" &&
                !Array.isArray(specs)
                    ? displayValue(
                        (
                        specs as Record<
                            string,
                            unknown
                        >
                        ).poles
                    )
                    : undefined;

              return (
                <button
                  type="button"
                  key={variant.id}
                  className={[
                    "akgp-node",
                    "variant-node",
                    selectedId === variant.id
                      ? "selected"
                      : "",
                  ].join(" ")}
                  onClick={() =>
                    setSelectedId(variant.id)
                  }
                >

                  <div className="variant-node-top">

                    <div className="node-icon">
                      ●
                    </div>

                    {poles && (
                      <span className="poles-badge">
                        {displayValue(poles)}
                      </span>
                    )}

                  </div>

                  <span className="node-type">
                    PRODUCT VARIANT
                  </span>

                  <strong className="mono">
                    {getEntityName(variant)}
                  </strong>

                  <small>
                    {shortId(variant.id)}
                  </small>

                </button>
              );
            })}

          </div>

        </div>


        {/* ===================================================
            GRAPH LEGEND
            =================================================== */}

        <div className="akgp-legend">

          <span>
            <i className="legend-dot manufacturer" />
            Manufacturer
          </span>

          <span>
            <i className="legend-dot family" />
            Product family
          </span>

          <span>
            <i className="legend-dot variant" />
            Variant
          </span>

        </div>

      </div>


      {/* =====================================================
          ENTITY INSPECTOR
          ===================================================== */}

      {selectedEntity && (

        <div className="akgp-inspector">

          <div className="inspector-header">

            <div>

              <span className="inspector-eyebrow">
                SELECTED ENTITY
              </span>

              <h3>
                {selectedEntity.type}
              </h3>

            </div>

            <button
              type="button"
              className="inspector-close"
              onClick={() =>
                setSelectedId(null)
              }
              aria-label="Close entity details"
            >
              ×
            </button>

          </div>


          <div className="inspector-id mono">
            {selectedEntity.id}
          </div>


          {/* PROPERTIES */}

          <div className="inspector-properties">

            {Object.entries(
              selectedEntity.properties ?? {}
            ).map(([key, value]) => (

              <div
                className="inspector-property"
                key={key}
              >

                <span>
                  {formatFieldName(key)}
                </span>

                <strong>
                  {displayValue(value)}
                </strong>

              </div>

            ))}

          </div>


          {/* RELATIONSHIPS */}

          <div className="inspector-relations">

            <span className="inspector-section-label">
              RELATIONSHIPS
            </span>

            {selectedRelationships.length > 0 ? (

              <div className="relation-list">

                {selectedRelationships.map(
                  (relationship, index) => {

                    const isSource =
                      relationship.source ===
                      selectedEntity.id;

                    const connectedId =
                      isSource
                        ? relationship.target
                        : relationship.source;

                    return (
                      <div
                        className="relation-row"
                        key={`${relationship.type}-${index}`}
                      >

                        <span className="relation-entity">
                          {shortId(connectedId)}
                        </span>

                        <strong>
                          {relationship.type}
                        </strong>

                        <span className="relation-direction">
                          {isSource
                            ? "→"
                            : "←"}
                        </span>

                      </div>
                    );
                  }
                )}

              </div>

            ) : (

              <p className="no-relations">
                No relationships available.
              </p>

            )}

          </div>

        </div>

      )}

    </div>
  );
}