from fastapi import FastAPI

app = FastAPI(
    title = "ZUT Ai assistant",
    description = "A RAG-powered AI assistant for ZUT students",
    version = "1.0.0",
)

@app.get("/")
def home():
    return {
        "message": "Welcome to ZUT Ai",
        "status": "running"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }