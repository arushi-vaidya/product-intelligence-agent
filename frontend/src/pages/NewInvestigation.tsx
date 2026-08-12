import {
  ArrowLeft,
  ArrowRight,
  Check,
  Circle,
  Search,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

import {
  createInvestigation,
  getInvestigation,
} from "../services/api";

export const stages = [
  "Intake",
  "Research",
  "Source Validation",
  "Document Extraction",
  "Specification Extraction",
  "Conflict Resolution",
  "AKGP",
  "Canonical Resolution",
  "Enrichment",
  "Evidence Validation",
  "Product Intelligence",
];

function NewInvestigation() {
  const navigate = useNavigate();

  const [manufacturer, setManufacturer] = useState("");
  const [mpn, setMpn] = useState("");

  const [running, setRunning] = useState(false);
  const [activeStage, setActiveStage] = useState(-1);
  const [error, setError] = useState("");

  const startInvestigation = async () => {
    if (!manufacturer.trim() || !mpn.trim()) {
      setError(
        "Please enter both manufacturer and product."
      );
      return;
    }

    setError("");
    setRunning(true);

    try {
      const created =
        await createInvestigation({
          manufacturer: manufacturer.trim(),
          mpn: mpn.trim(),
        });

      await pollInvestigation(
        created.investigation_id
      );
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Investigation failed."
      );

      setRunning(false);
    }
  };

  const pollInvestigation = async (
    investigationId: string
  ) => {
    const poll = async (): Promise<void> => {
      const investigation =
        await getInvestigation(
          investigationId
        );

      updatePipeline(investigation.tasks);

      if (investigation.status === "done") {
        navigate(
          `/investigate/${investigationId}`
        );

        return;
      }

      if (investigation.status === "failed") {
        throw new Error(
          "Investigation failed."
        );
      }

      await new Promise((resolve) =>
        setTimeout(resolve, 1200)
      );

      return poll();
    };

    await poll();
  };

  const updatePipeline = (
    tasks: {
      agent: string;
      status: string;
    }[]
  ) => {
    if (!tasks.length) {
      return;
    }

    const completed =
      tasks.filter(
        (task) => task.status === "done"
      ).length;

    const runningTask =
      tasks.find(
        (task) => task.status === "running"
      );

    if (runningTask) {
      const index = getStageIndex(
        runningTask.agent
      );

      if (index >= 0) {
        setActiveStage(index);
        return;
      }
    }

    setActiveStage(
      Math.min(
        completed,
        stages.length - 1
      )
    );
  };

  return (
    <main className="page-shell investigation-page">
      <header className="page-header compact">
        <button
          className="back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={17} />
          Back
        </button>

        <div>
          <div className="eyebrow">
            NEW INVESTIGATION
          </div>

          <h1>
            {running
              ? "Investigation in progress"
              : "Investigate a product"}
          </h1>

          <p>
            {running
              ? `${manufacturer} · ${mpn}`
              : "Give us a manufacturer and product identifier."}
          </p>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {!running ? (
        <section className="investigation-layout">
          <div className="investigation-form-panel">
            <div className="panel-label">
              PRODUCT IDENTIFICATION
            </div>

            <label>
              Manufacturer
            </label>

            <div className="input-wrapper">
              <Search size={17} />

              <input
                value={manufacturer}
                onChange={(event) =>
                  setManufacturer(
                    event.target.value
                  )
                }
                placeholder="e.g. Schneider Electric"
              />
            </div>

            <label>
              Product / MPN
            </label>

            <div className="input-wrapper">
              <Search size={17} />

              <input
                value={mpn}
                onChange={(event) =>
                  setMpn(event.target.value)
                }
                placeholder="e.g. iC60N C20"
              />
            </div>

            <button
              className="primary-button full-width"
              onClick={startInvestigation}
            >
              Begin Investigation
              <ArrowRight size={17} />
            </button>
          </div>

          <Pipeline
            stages={stages}
            activeStage={-1}
          />
        </section>
      ) : (
        <section className="running-investigation">
          <Pipeline
            stages={stages}
            activeStage={activeStage}
          />

          <div className="running-message">
            <div className="pulse-ring" />

            <div>
              <div className="panel-label">
                INTELLIGENCE ENGINE
              </div>

              <h2>
                Agents are investigating the
                product.
              </h2>

              <p>
                Researching sources, extracting
                specifications, resolving variants
                and building the knowledge graph.
              </p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

function getStageIndex(agent: string) {
  const normalized = agent
    .toLowerCase()
    .replace(/_agent$/, "")
    .replace(/_/g, " ");

  return stages.findIndex(
    (stage) =>
      normalized.includes(
        stage.toLowerCase()
      )
  );
}

function Pipeline({
  stages,
  activeStage,
}: {
  stages: string[];
  activeStage: number;
}) {
  return (
    <div className="pipeline-panel">
      <div className="panel-label">
        INVESTIGATION PIPELINE
      </div>

      <div className="pipeline">
        {stages.map((stage, index) => {
          const complete =
            index < activeStage;

          const active =
            index === activeStage;

          return (
            <div
              className="pipeline-stage"
              key={stage}
            >
              <div
                className={`pipeline-icon ${
                  complete
                    ? "complete"
                    : active
                      ? "active"
                      : ""
                }`}
              >
                {complete ? (
                  <Check size={14} />
                ) : (
                  <Circle size={9} />
                )}
              </div>

              <span
                className={
                  active
                    ? "pipeline-stage-active"
                    : ""
                }
              >
                {stage}
              </span>

              {index !==
                stages.length - 1 && (
                <div
                  className={`pipeline-connector ${
                    complete
                      ? "complete"
                      : ""
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default NewInvestigation;