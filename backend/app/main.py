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

    return {
        "investigation_id": investigation.id,
        "status": investigation.status.value,
        "input": investigation.input_data,
        "tasks": [
            {
                "id": task.id,
                "agent": task.agent_name,
                "status": task.status.value,
                "attempts": task.attempts,
                "depends_on": task.depends_on,
                "output": task.output_data,
            }
            for task in tasks
        ],
    }