from fastapi import FastAPI

app = FastAPI(
    title="OmniSight AI Self-Healing API",
    description="AI-powered UI self-healing and browser recovery",
    version="1.0.0"
)


@app.get("/")
async def home():
    return {
        "message": "OmniSight AI Self-Healing API is running!",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }