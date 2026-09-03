import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  LoaderCircle,
  X,
} from "lucide-react";
import {
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";
import { useNavigate } from "react-router-dom";

import { runBulkExcelInvestigation } from "../services/api";

const ACCEPTED_EXTENSIONS = [
  ".xlsx",
  ".xlsm",
  ".csv",
];

function isAcceptedFile(file: File) {
  const name = file.name.toLowerCase();

  return ACCEPTED_EXTENSIONS.some((extension) =>
    name.endsWith(extension)
  );
}

function BulkUpload() {
  const navigate = useNavigate();
  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const [sheetFile, setSheetFile] =
    useState<File | null>(null);

  const [processing, setProcessing] =
    useState(false);
  const [error, setError] = useState("");

  const [resultBlob, setResultBlob] =
    useState<Blob | null>(null);
  const [resultUrl, setResultUrl] =
    useState<string | null>(null);

  const handleFileSelection = (
    file: File | null
  ) => {
    if (!file) {
      return;
    }

    if (!isAcceptedFile(file)) {
      setError(
        "Please upload a .xlsx, .xlsm, or .csv file."
      );
      return;
    }

    setError("");
    setSheetFile(file);
    clearResult();
  };

  const handleFileInputChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0] ?? null;

    handleFileSelection(file);
    event.target.value = "";
  };

  const handleDrop = (
    event: DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();

    const file =
      event.dataTransfer.files?.[0] ?? null;

    handleFileSelection(file);
  };

  const clearResult = () => {
    if (resultUrl) {
      URL.revokeObjectURL(resultUrl);
    }

    setResultBlob(null);
    setResultUrl(null);
  };

  const clearSheet = () => {
    setSheetFile(null);
    clearResult();
  };

  const processSheet = async () => {
    if (!sheetFile) {
      setError(
        "Upload a spreadsheet before generating the filled sheet."
      );
      return;
    }

    setError("");
    setProcessing(true);
    clearResult();

    try {
      const blob = await runBulkExcelInvestigation(
        sheetFile
      );

      const url = URL.createObjectURL(blob);

      setResultBlob(blob);
      setResultUrl(url);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Bulk investigation failed."
      );
    } finally {
      setProcessing(false);
    }
  };

  const downloadResult = () => {
    if (!resultUrl) {
      return;
    }

    const link = document.createElement("a");
    link.href = resultUrl;
    link.download = "delivery_format_output.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
            BULK UPLOAD
          </div>

          <h1>Bulk investigate from a sheet</h1>

          <p>
            Upload an Excel or CSV sheet of products
            and get back the same Delivery Format
            sheet, filled in by the pipeline.
          </p>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <section className="investigation-layout">
        <div className="investigation-form-panel">
          <div className="panel-label">
            PRODUCT SHEET
          </div>

          <div className="target-intro">
            <h2>Upload your sheet</h2>
            <p>
              Include the same columns as the sample
              dataset: Mfg_Part_Num, Part_Desc,
              E1_Brand, Unilog_Brand, DIB_Brand, and
              Part_Manuf. Every row is run through the
              exact same investigation pipeline as a
              single manual lookup.
            </p>
          </div>

          <div className="image-upload-section">
            <label>
              Upload product sheet
            </label>

            <div
              className={`image-upload-dropzone${
                sheetFile ? " has-preview" : ""
              }`}
              onDragOver={(event) =>
                event.preventDefault()
              }
              onDrop={handleDrop}
              onClick={() => {
                if (!sheetFile) {
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
                accept={ACCEPTED_EXTENSIONS.join(
                  ","
                )}
                hidden
                onChange={
                  handleFileInputChange
                }
              />

              {sheetFile ? (
                <div className="image-upload-preview sheet-preview">
                  <FileSpreadsheet size={22} />

                  <span>{sheetFile.name}</span>

                  <button
                    type="button"
                    className="image-upload-clear"
                    onClick={(event) => {
                      event.stopPropagation();
                      clearSheet();
                    }}
                    aria-label="Remove uploaded sheet"
                  >
                    <X size={14} />
                  </button>
                </div>
              ) : (
                <>
                  <FileSpreadsheet size={18} />

                  <div className="image-upload-copy">
                    <strong>
                      Upload a product sheet
                    </strong>

                    <span>
                      Drop or browse · XLSX, XLSM, CSV
                    </span>
                  </div>
                </>
              )}
            </div>

            <button
              type="button"
              className="secondary-button full-width image-extract-button"
              onClick={processSheet}
              disabled={
                !sheetFile || processing
              }
            >
              {processing ? (
                <>
                  <LoaderCircle
                    size={17}
                    className="spin-icon"
                  />
                  Running pipeline on every row...
                </>
              ) : (
                <>
                  Generate filled sheet
                  <FileSpreadsheet size={17} />
                </>
              )}
            </button>

            {processing ? (
              <p className="extraction-note">
                This runs the full investigation
                pipeline for each row, so larger
                sheets can take a while. Keep this
                tab open until it finishes.
              </p>
            ) : null}

            {resultBlob ? (
              <div className="ready-badge bulk-ready-badge">
                <span />
                <CheckCircle2 size={15} />
                Delivery Format sheet ready · {(
                  resultBlob.size / 1024
                ).toFixed(0)}{" "}
                KB
              </div>
            ) : null}

            {resultUrl ? (
              <button
                type="button"
                className="primary-button full-width"
                onClick={downloadResult}
              >
                <Download size={17} />
                Download filled sheet
              </button>
            ) : null}
          </div>
        </div>

        <div className="pipeline-panel bulk-info-panel">
          <div className="panel-label">
            HOW IT WORKS
          </div>

          <ul className="bulk-steps">
            <li>
              <strong>1. Upload</strong>
              <span>
                Drop in an .xlsx or .csv sheet with
                one row per product.
              </span>
            </li>

            <li>
              <strong>2. Investigate</strong>
              <span>
                Each row is sent through the same
                DFOO pipeline as a manual
                investigation - research,
                specification extraction, enrichment,
                and validation.
              </span>
            </li>

            <li>
              <strong>3. Download</strong>
              <span>
                Get back one .xlsx in the Delivery
                Format, with every column the
                pipeline could fill in already
                populated.
              </span>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}

export default BulkUpload;
