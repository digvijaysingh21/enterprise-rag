from fastapi import FastAPI

app = FastAPI(title="Eneterprise RAG Platform")

@app.get("/health")
def health_check():
    return {"status": "ok"}