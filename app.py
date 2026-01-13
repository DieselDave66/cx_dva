import time
from typing import Dict
import uvicorn
from errors.handlers import register_exception_handlers
from routes import api_router
from fastapi import FastAPI, Request

app = FastAPI(
    title="FastAPI & Databricks Apps",
    description="A simple FastAPI application example for Databricks Apps runtime",
    version="1.0.0",
)

register_exception_handlers(app)
app.include_router(api_router)

@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "app": "Databricks FastAPI",
        "message": "Welcome to API",
        "docs": "/docs",
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)