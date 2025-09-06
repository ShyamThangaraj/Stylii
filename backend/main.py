from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime

app = FastAPI(title="Nano Banana Hackathon API", version="1.0.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/status")
async def status_check():
    """Detailed status endpoint for frontend to check backend health"""
    return {
        "status": "running",
        "service": "FastAPI Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
