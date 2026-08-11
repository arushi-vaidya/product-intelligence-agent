from fastapi import FastAPI, HTTPException

from app.dfoo.orchestrator import DFOO


app = FastAPI(
    title="Industrial Product Intelligence"
)


dfoo = DFOO()


@app.get("/")
async def root():

    return {
        "message": (
            "Industrial Product Intelligence "
            "API is running"
        )
    }


@app.post("/investigate")
async def investigate(product: dict):

    investigation = (
        await dfoo.start_investigation(
            product
        )
    )

    return {
        "investigation_id": investigation.id,
        "status": investigation.status.value,
    }


@app.get("/investigate/{investigation_id}")
async def get_investigation(
    investigation_id: str
):

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

    tasks = (
        dfoo.task_repository
        .get_tasks_for_investigation(
            investigation_id
        )
    )

    # Find the final Product Intelligence task
    final_task = next(
        (
            task
            for task in tasks
            if task.agent_name
            == "product_intelligence_agent"
        ),
        None,
    )

    # Pipeline has not reached final agent yet
    if final_task is None:

        return {
            "investigation_id": investigation.id,
            "status": investigation.status.value,
            "input": investigation.input_data,
            "result": None,
        }

    output = final_task.output_data or {}

    return {
        "investigation_id": investigation.id,
        "status": investigation.status.value,
        "input": investigation.input_data,
        "result": output.get(
            "data",
            {}
        ),
    }