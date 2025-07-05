import os
import aiohttp
import asyncio
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"
RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "15"))

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_KEY environment variable is required")

# Initialize FastAPI app
app = FastAPI(
    title="OpenAI API Proxy",
    description="Proxy service for OpenAI API with rate limiting",
    version="1.0.0"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP session for OpenAI API calls
http_session: Optional[aiohttp.ClientSession] = None

@app.on_event("startup")
async def startup_event():
    """Initialize HTTP session on startup"""
    global http_session
    timeout = aiohttp.ClientTimeout(total=60)
    http_session = aiohttp.ClientSession(timeout=timeout)
    logger.info("HTTP session initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP session on shutdown"""
    global http_session
    if http_session:
        await http_session.close()
    logger.info("HTTP session closed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "openai-proxy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OpenAI API Proxy", "version": "1.0.0"}

async def proxy_request(
    request: Request,
    path: str,
    method: str = "POST"
) -> JSONResponse:
    """Proxy request to OpenAI API"""
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "OpenAI-Python/1.3.5",
        "OpenAI-Beta": "assistants=v2"
    }
    
    # Get request body
    try:
        body = await request.body()
        if body:
            data = json.loads(body.decode())
        else:
            data = None
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    # Make request to OpenAI API
    url = f"{OPENAI_BASE_URL}/{path}"
    
    try:
        async with http_session.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None
        ) as response:
            
            # Handle streaming responses
            if response.headers.get("content-type", "").startswith("text/plain"):
                async def generate():
                    async for chunk in response.content.iter_chunked(1024):
                        yield chunk
                
                return StreamingResponse(
                    generate(),
                    media_type=response.headers.get("content-type", "text/plain"),
                    status_code=response.status
                )
            
            # Handle JSON responses
            else:
                response_data = await response.json()
                return JSONResponse(
                    content=response_data,
                    status_code=response.status
                )
                
    except aiohttp.ClientError as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise HTTPException(status_code=500, detail="Error calling OpenAI API")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# OpenAI API endpoints
@app.post("/v1/chat/completions")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def chat_completions(request: Request):
    """Proxy chat completions endpoint"""
    return await proxy_request(request, "chat/completions")

@app.post("/v1/assistants")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def create_assistant(request: Request):
    """Proxy create assistant endpoint"""
    return await proxy_request(request, "assistants")

@app.get("/v1/assistants/{assistant_id}")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def get_assistant(request: Request, assistant_id: str):
    """Proxy get assistant endpoint"""
    return await proxy_request(request, f"assistants/{assistant_id}", "GET")

@app.post("/v1/threads")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def create_thread(request: Request):
    """Proxy create thread endpoint"""
    return await proxy_request(request, "threads")

@app.post("/v1/threads/{thread_id}/messages")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def create_message(request: Request, thread_id: str):
    """Proxy create message endpoint"""
    return await proxy_request(request, f"threads/{thread_id}/messages")

@app.post("/v1/threads/{thread_id}/runs")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def create_run(request: Request, thread_id: str):
    """Proxy create run endpoint"""
    return await proxy_request(request, f"threads/{thread_id}/runs")

@app.get("/v1/threads/{thread_id}/runs/{run_id}")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def get_run(request: Request, thread_id: str, run_id: str):
    """Proxy get run endpoint"""
    return await proxy_request(request, f"threads/{thread_id}/runs/{run_id}", "GET")

@app.post("/v1/threads/{thread_id}/runs/{run_id}/submit_tool_outputs")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def submit_tool_outputs(request: Request, thread_id: str, run_id: str):
    """Proxy submit tool outputs endpoint"""
    return await proxy_request(request, f"threads/{thread_id}/runs/{run_id}/submit_tool_outputs")

@app.get("/v1/threads/{thread_id}/messages")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def list_messages(request: Request, thread_id: str):
    """Proxy list messages endpoint"""
    return await proxy_request(request, f"threads/{thread_id}/messages", "GET")

@app.get("/v1/models")
@limiter.limit(f"{RATE_LIMIT_RPS}/minute")
async def list_models(request: Request):
    """Proxy list models endpoint"""
    return await proxy_request(request, "models", "GET")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 