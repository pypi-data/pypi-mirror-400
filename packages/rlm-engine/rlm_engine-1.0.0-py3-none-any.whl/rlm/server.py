"""FastAPI server for RLM."""
import os
import time
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .core import RLM, RLMConfig, RLMResult
from .config import load_config, RLMSettings

logger = logging.getLogger(__name__)


class CompletionRequest(BaseModel):
    """Request body for completion endpoint."""
    query: str = Field(..., description="The question to answer")
    context: str = Field(..., description="The document to analyze")
    max_iterations: int = Field(default=10, ge=1, le=50)
    max_depth: int = Field(default=3, ge=1, le=5)
    temperature: float = Field(default=0.7, ge=0, le=2)


class CompletionResponse(BaseModel):
    """Response body for completion endpoint."""
    answer: str
    iterations: int
    llm_calls: int
    execution_time: float
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    model: str
    backend: str


# Global RLM instance
_rlm: Optional[RLM] = None
_settings: Optional[RLMSettings] = None


def get_rlm() -> RLM:
    """Get or create RLM instance."""
    global _rlm, _settings
    
    if _rlm is None:
        _settings = load_config()
        config = RLMConfig(
            max_iterations=_settings.max_iterations,
            max_depth=_settings.max_depth,
            temperature=_settings.temperature,
            max_tokens=_settings.max_tokens,
            verbose=_settings.verbose,
        )
        _rlm = RLM(
            backend=_settings.backend,
            model=_settings.model,
            base_url=_settings.base_url,
            api_key=_settings.api_key,
            config=config,
        )
        logger.info(f"Initialized RLM with backend={_settings.backend}, model={_settings.model}")
    
    return _rlm


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting RLM server...")
    yield
    global _rlm
    if _rlm:
        _rlm.close()
        logger.info("RLM server shutdown complete")


app = FastAPI(
    title="RLM API",
    description="Recursive Language Model API for unlimited context processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check server health."""
    settings = load_config()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model=settings.model or "default",
        backend=settings.backend,
    )


@app.post("/v1/rlm/completion", response_model=CompletionResponse)
async def completion(request: CompletionRequest):
    """
    Process a query over a document using RLM.
    
    The RLM will:
    1. Write Python code to analyze the document
    2. Execute the code
    3. Iterate until finding the answer
    """
    try:
        rlm = get_rlm()
        
        # Override config if specified
        if request.max_iterations != 10:
            rlm.config.max_iterations = request.max_iterations
        if request.max_depth != 3:
            rlm.config.max_depth = request.max_depth
        if request.temperature != 0.7:
            rlm.config.temperature = request.temperature
        
        result = rlm.completion(
            query=request.query,
            context=request.context,
        )
        
        return CompletionResponse(
            answer=result.answer,
            iterations=result.iterations,
            llm_calls=result.total_llm_calls,
            execution_time=result.execution_time,
            success=result.success,
            error=result.error,
        )
        
    except Exception as e:
        logger.exception("Error processing completion request")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/rlm/completion/async")
async def completion_async(request: CompletionRequest, background_tasks: BackgroundTasks):
    """Start an async completion job (for long-running tasks)."""
    job_id = f"job_{int(time.time() * 1000)}"
    # In a real implementation, you'd store job status in Redis/DB
    return {"job_id": job_id, "status": "queued"}


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
