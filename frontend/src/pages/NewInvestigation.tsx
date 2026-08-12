import {
  ArrowLeft,
  ArrowRight,
  Check,
  Circle,
  ImagePlus,
  LoaderCircle,
  Search,
  X,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";
import { useNavigate } from "react-router-dom";

import {
  createInvestigation,
  extractProductFromImage,
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

const ACCEPTED_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
];

function NewInvestigation() {
  const navigate = useNavigate();
  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const [manufacturer, setManufacturer] =
    useState("");
  const [mpn, setMpn] = useState("");

  const [imageFile, setImageFile] =
    useState<File | null>(null);
  const [imagePreview, setImagePreview] =
    useState<string | null>(null);

  const [extracting, setExtracting] =
    useState(false);
  const [extractionNote, setExtractionNote] =
    useState("");

  const [running, setRunning] = useState(false);
  const [activeStage, setActiveStage] =
    useState(-1);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!imageFile) {
      setImagePreview(null);
      return;
    }

    const previewUrl =
      URL.createObjectURL(imageFile);

    setImagePreview(previewUrl);

    return () => {
      URL.revokeObjectURL(previewUrl);
    };
  }, [imageFile]);

  const handleImageSelection = (
    file: File | null
  ) => {
    if (!file) {
      return;
    }

    if (
      !ACCEPTED_IMAGE_TYPES.includes(
        file.type
      )
    ) {
      setError(
        "Please upload a JPEG, PNG, WebP, or GIF image."
      );
      return;
    }

    setError("");
    setExtractionNote("");
    setImageFile(file);
  };

  const handleFileInputChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0] ?? null;

    handleImageSelection(file);
    event.target.value = "";
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();

    const file =
      event.dataTransfer.files?.[0] ?? null;

    handleImageSelection(file);
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    setExtractionNote("");
  };

  const extractFromImage = async () => {
    if (!imageFile) {
      setError(
        "Upload an image before extracting product details."
      );
      return;
    }

    setError("");
    setExtractionNote("");
    setExtracting(true);

    try {
      const extracted =
        await extractProductFromImage(
          imageFile
        );

      if (extracted.manufacturer) {
        setManufacturer(
          extracted.manufacturer
        );
      }

      if (extracted.mpn) {
        setMpn(extracted.mpn);
      }

      if (
        !extracted.manufacturer &&
        !extracted.mpn
      ) {
        throw new Error(
          "Could not extract a manufacturer or product from the image."
        );
      }

      setExtractionNote(
        extracted.notes ||
          "Product details extracted from image. Review before starting the investigation."
      );
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Image extraction failed."
      );
    } finally {
      setExtracting(false);
    }
  };

  const startInvestigation = async () => {
    if (
      !manufacturer.trim() ||
      !mpn.trim()
    ) {
      setError(
        "Please enter both manufacturer and product, or upload an image and extract the details."
      );
      return;
    }

    setError("");
    setRunning(true);

    try {
      const created =
        await createInvestigation({
          manufacturer:
            manufacturer.trim(),
          mpn: mpn.trim(),
        });

      await pollInvestigation(
        created.investigation_id
      );
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
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

      if (
        investigation.status === "done"
      ) {
        navigate(
          `/investigate/${investigationId}`
        );

        return;
      }

      if (
        investigation.status === "failed"
      ) {
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
        (task) =>
          task.status === "running"
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
              : "Enter details manually or upload a product image for Gemini to read."}
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

            <div className="target-intro">
              <h2>Define the target</h2>
              <p>
                Provide the manufacturer and
                product / MPN identifier, or
                upload a photo of the product
                or nameplate and let Gemini
                extract the details.
              </p>
            </div>

            <div className="image-upload-section">
              <label>
                Upload product image
              </label>

              <div
                className={`image-upload-dropzone${
                  imagePreview
                    ? " has-preview"
                    : ""
                }`}
                onDragOver={(event) =>
                  event.preventDefault()
                }
                onDrop={handleDrop}
                onClick={() => {
                  if (!imagePreview) {
                    fileInputRef.current?.click();
                  }
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();
                    fileInputRef.current?.click();
                  }
                }}
                role="button"
                tabIndex={0}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={ACCEPTED_IMAGE_TYPES.join(
                    ","
                  )}
                  hidden
                  onChange={
                    handleFileInputChange
                  }
                />

                {imagePreview ? (
                  <div className="image-upload-preview">
                    <img
                      src={imagePreview}
                      alt="Uploaded product preview"
                    />

                    <button
                      type="button"
                      className="image-upload-clear"
                      onClick={(event) => {
                        event.stopPropagation();
                        clearImage();
                      }}
                      aria-label="Remove uploaded image"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <>
                    <ImagePlus size={18} />

                    <div className="image-upload-copy">
                      <strong>
                        Upload a product image
                      </strong>

                      <span>
                        Drop or browse · JPEG, PNG, WebP, GIF · 10 MB max
                      </span>
                    </div>
                  </>
                )}
              </div>

              <button
                type="button"
                className="secondary-button full-width image-extract-button"
                onClick={extractFromImage}
                disabled={
                  !imageFile || extracting
                }
              >
                {extracting ? (
                  <>
                    <LoaderCircle
                      size={17}
                      className="spin-icon"
                    />
                    Extracting with Gemini...
                  </>
                ) : (
                  <>
                    Extract manufacturer &amp; product
                    <ArrowRight size={17} />
                  </>
                )}
              </button>

              {extractionNote ? (
                <p className="extraction-note">
                  {extractionNote}
                </p>
              ) : null}
            </div>

            <div className="input-divider">
              <span>or enter manually</span>
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

const AGENT_TO_STAGE: Record<string, string> = {
  intake_agent: "Intake",
  research_agent: "Research",
  source_validation_agent: "Source Validation",
  document_agent: "Document Extraction",
  specification_agent: "Specification Extraction",
  conflict_agent: "Conflict Resolution",
  akgp_agent: "AKGP",
  canonical_resolution_agent: "Canonical Resolution",
  enrichment_agent: "Enrichment",
  evidence_validation_agent: "Evidence Validation",
  product_intelligence_agent: "Product Intelligence",
};

function getStageIndex(agent: string) {
  const stage = AGENT_TO_STAGE[agent.toLowerCase()];

  if (stage) {
    return stages.indexOf(stage);
  }

  const normalized = agent
    .toLowerCase()
    .replace(/_agent$/, "")
    .replace(/_/g, " ");

  return stages.findIndex(
    (stage) =>
      normalized.includes(stage.toLowerCase()) ||
      stage.toLowerCase().includes(normalized)
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
