from typing import Any, Optional

import io
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.dfoo.orchestrator import DFOO

from app.schemas.api import (
    InvestigationRequest,
    InvestigationCreatedResponse,
    InvestigationListResponse,
    InvestigationResponse,
    InvestigationSummary,
    ProductExtractionResponse,
    ProductIntelligenceResponse,
    TaskResponse,
)
from app.services.product_image_extractor import (
    ProductImageExtractionError,
    extract_product_from_image,
)
from app.services.bulk_excel_service import (
    BulkExcelError,
    bulk_investigation_repository,
    start_bulk_excel_investigation,
)


# ==========================================
# APP
# ==========================================

app = FastAPI(
    title="Industrial Product Intelligence",
    version="0.1.0",
    description=(
        "AI-powered industrial product intelligence "
        "and enrichment pipeline."
    ),
)


load_dotenv()


def get_cors_origins() -> list[str]:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    frontend_url = os.getenv("FRONTEND_URL")

    if frontend_url:
        origins.append(
            frontend_url.rstrip("/")
        )

    extra_origins = os.getenv(
        "CORS_ORIGINS",
        "",
    )

    for origin in extra_origins.split(","):
        cleaned = origin.strip().rstrip("/")

        if cleaned and cleaned not in origins:
            origins.append(cleaned)

    return origins


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=(
        r"https://.*\.vercel\.app"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DFOO
# ==========================================

dfoo = DFOO()


def build_investigation_summary(
    investigation,
) -> InvestigationSummary:
    input_data = investigation.input_data or {}
    product_intelligence: dict[str, Any] = {}

    if investigation.result:
        product_intelligence = (
            investigation.result.get(
                "product_intelligence",
                investigation.result,
            )
            or {}
        )

    sources = product_intelligence.get(
        "sources",
        [],
    )
    variants = product_intelligence.get(
        "variants",
        [],
    )

    source_ids: set[str] = set()

    for source in sources:
        if isinstance(source, dict):
            source_id = source.get("id")

            if source_id:
                source_ids.add(source_id)

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        for source_id in variant.get(
            "sources",
            [],
        ):
            if source_id:
                source_ids.add(source_id)

    commerce_readiness = product_intelligence.get(
        "commerce_readiness",
        {},
    )

    return InvestigationSummary(
        investigation_id=investigation.id,
        status=investigation.status.value,
        manufacturer=input_data.get(
            "manufacturer",
            "",
        ),
        mpn=input_data.get(
            "mpn",
            "",
        ),
        product_category=product_intelligence.get(
            "product_category"
        ),
        source_count=len(source_ids),
        variant_count=len(variants),
        commerce_readiness=commerce_readiness.get(
            "status"
        ),
        created_at=investigation.created_at,
    )


# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():

    return {
        "message": (
            "Industrial Product Intelligence "
            "API is running"
        )
    }


# ==========================================
# CREATE INVESTIGATION
# ==========================================

@app.post(
    "/investigate",
    response_model=InvestigationCreatedResponse,
)
async def investigate(
    product: InvestigationRequest,
):

    investigation = (
        await dfoo.start_investigation(
            product.model_dump()
        )
    )

    return InvestigationCreatedResponse(
        investigation_id=investigation.id,
        status=investigation.status.value,
    )


# ==========================================
# LIST INVESTIGATIONS
# ==========================================

@app.get(
    "/investigations",
    response_model=InvestigationListResponse,
)
async def list_investigations(
    q: Optional[str] = None,
):

    investigations = (
        dfoo.investigation_repository.list_all()
    )

    summaries = [
        build_investigation_summary(
            investigation
        )
        for investigation in investigations
    ]

    if q:
        query = q.strip().lower()

        if query:
            summaries = [
                summary
                for summary in summaries
                if query in summary.manufacturer.lower()
                or query in summary.mpn.lower()
                or query in (
                    summary.product_category or ""
                ).lower()
            ]

    return InvestigationListResponse(
        investigations=summaries
    )


# ==========================================
# EXTRACT PRODUCT FROM IMAGE
# ==========================================

@app.post(
    "/investigate/extract-from-image",
    response_model=ProductExtractionResponse,
)
async def extract_product_from_image_endpoint(
    file: UploadFile = File(...),
):

    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Could not determine image type.",
        )

    image_bytes = await file.read()

    try:
        extracted = extract_product_from_image(
            image_bytes=image_bytes,
            mime_type=file.content_type,
        )
    except ProductImageExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return ProductExtractionResponse(
        **extracted
    )


# ==========================================
# BULK EXCEL / CSV INVESTIGATION
#
# Accepts a spreadsheet of products, runs each
# row through the SAME DFOO pipeline used by a
# single manual investigation (nothing about the
# pipeline itself is changed here), and streams
# back a filled-in Delivery Format .xlsx.
# ==========================================

@app.post("/investigate/bulk-excel")
async def bulk_excel_investigate(
    file: UploadFile = File(...),
):

    content = await file.read()

    try:
        job = start_bulk_excel_investigation(
            dfoo=dfoo,
            filename=file.filename or "",
            content=content,
        )
    except BulkExcelError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {
        "bulk_investigation_id": job.id,
        "status": job.status,
    }


@app.get("/investigate/bulk-excel/{bulk_investigation_id}")
async def get_bulk_excel_investigation(
    bulk_investigation_id: str,
):
    job = bulk_investigation_repository.get(
        bulk_investigation_id
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Bulk investigation not found.",
        )

    return {
        "bulk_investigation_id": job.id,
        "status": job.status,
        "error": job.error,
    }


@app.get(
    "/investigate/bulk-excel/{bulk_investigation_id}/download"
)
async def download_bulk_excel_investigation(
    bulk_investigation_id: str,
):
    job = bulk_investigation_repository.get(
        bulk_investigation_id
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Bulk investigation not found.",
        )

    if job.status == "failed":
        raise HTTPException(
            status_code=500,
            detail=job.error or "Bulk investigation failed.",
        )

    if job.status != "done" or job.workbook_bytes is None:
        raise HTTPException(
            status_code=409,
            detail="Bulk investigation is still running.",
        )

    output_filename = "delivery_format_output.xlsx"

    return StreamingResponse(
        io.BytesIO(job.workbook_bytes),
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{output_filename}"'
            )
        },
    )


# ==========================================
# GET FULL INVESTIGATION
# ==========================================

@app.get(
    "/investigate/{investigation_id}",
    response_model=InvestigationResponse,
)
async def get_investigation(
    investigation_id: str,
):

    # --------------------------------------
    # Find investigation
    # --------------------------------------

    investigation = (
        dfoo.investigation_repository.get(
            investigation_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    # --------------------------------------
    # Get tasks
    # --------------------------------------

    tasks = (
        dfoo.task_repository
        .get_tasks_for_investigation(
            investigation_id
        )
    )

    # --------------------------------------
    # Get result
    # --------------------------------------

    result = None

    if investigation.result:

        result = investigation.result.get(
            "product_intelligence",
            investigation.result,
        )

    # --------------------------------------
    # Build response
    # --------------------------------------

    return InvestigationResponse(

        investigation_id=investigation.id,

        status=investigation.status.value,

        input=InvestigationRequest(
            **investigation.input_data
        ),

        result=result,

        tasks=[
            TaskResponse(
                id=task.id,
                agent=task.agent_name,
                status=task.status.value,
                attempts=task.attempts,
                depends_on=task.depends_on,
                output=task.output_data or None,
            )
            for task in tasks
        ],
    )


# ==========================================
# GET CLEAN PRODUCT INTELLIGENCE
# ==========================================

@app.get(
    "/investigate/{investigation_id}/result",
    response_model=ProductIntelligenceResponse,
)
async def get_investigation_result(
    investigation_id: str,
):

    # --------------------------------------
    # Find investigation
    # --------------------------------------

    investigation = (
        dfoo.investigation_repository.get(
            investigation_id
        )
    )

    if investigation is None:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    # --------------------------------------
    # Check result
    # --------------------------------------

    if not investigation.result:

        raise HTTPException(
            status_code=404,
            detail="Investigation result not available",
        )

    # --------------------------------------
    # Extract product intelligence
    # --------------------------------------

    product_intelligence = (
        investigation.result.get(
            "product_intelligence"
        )
    )

    if not product_intelligence:

        raise HTTPException(
            status_code=404,
            detail=(
                "Product intelligence not available"
            ),
        )

    # --------------------------------------
    # Return clean result
    # --------------------------------------

    return ProductIntelligenceResponse(
        **product_intelligence
    )
