from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="Eneterprise RAG Platform")

@app.get("/health")
def health_check():
    return {"status": "ok",
            "environment": settings.ENVIRONMENT,
            }