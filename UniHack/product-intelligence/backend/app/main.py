from fastapi import FastAPI
from app.dfoo.orchestrator import DFOO


app = FastAPI(
    title="Industrial Product Intelligence"
)

dfoo = DFOO()


@app.get("/")
async def root():
    return {
        "message": "Product Intelligence API is running"
    }


@app.post("/investigate")
async def investigate(product: dict):

    result = await dfoo.start_investigation(product)

    return result