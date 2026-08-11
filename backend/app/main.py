from fastapi import FastAPI, HTTPException

from app.dfoo.orchestrator import DFOO

from app.schemas.api import (
    InvestigationRequest,
    InvestigationCreatedResponse,
    InvestigationResponse,
    ProductIntelligenceResponse,
    TaskResponse,
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


dfoo = DFOO()


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
    # Get all tasks
    # --------------------------------------

    tasks = (
        dfoo.task_repository
        .get_tasks_for_investigation(
            investigation_id
        )
    )

    # --------------------------------------
    # Unwrap final product intelligence
    # --------------------------------------
    #
    # The final ProductIntelligenceAgent
    # returns:
    #
    # {
    #     "product_intelligence": {
    #         ...
    #     }
    # }
    #
    # The API response model expects the
    # inner object directly.
    # --------------------------------------

    result = None

    if investigation.result:

        result = investigation.result.get(
            "product_intelligence",
            investigation.result,
        )

    # --------------------------------------
    # Build API response
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
                output=task.output_data,
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
    # Check whether result exists
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
    # Return clean product intelligence
    # --------------------------------------

    return ProductIntelligenceResponse(
        **product_intelligence
    )