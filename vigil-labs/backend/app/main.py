"""
VIGIL LABS - Main Application
FastAPI application entry point with production-grade middleware,
CORS, WebSocket, security headers, and lifecycle management.
"""
import json
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db, AsyncSessionLocal
from app.core.security import decode_token
from app.core.middleware import register_exception_handlers
from app.api.routes import auth, tools, execution, system, store, workflows
from app.api.websocket.terminal import ws_manager

logger = logging.getLogger("vigil_labs.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    
    # Startup
    await init_db()
    
    # Seed store catalog on first run
    from app.services.store_catalog import TOOL_CATALOG
    from app.models.store import StoreTool
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(StoreTool).limit(1))
        if not result.scalar_one_or_none():
            for tool_data in TOOL_CATALOG:
                st = StoreTool(
                    name=tool_data["name"], slug=tool_data["slug"],
                    category=tool_data["category"], description=tool_data.get("description", ""),
                    executable_name=tool_data.get("executable_name"),
                    install_method=tool_data.get("install_method", "manual"),
                    install_command_linux=tool_data.get("install_command_linux"),
                    install_command_windows=tool_data.get("install_command_windows"),
                    install_command_macos=tool_data.get("install_command_macos"),
                    github_repo=tool_data.get("github_repo"),
                    github_url=tool_data.get("github_url"),
                    risk_level=tool_data.get("risk_level", "medium"),
                    supports_linux=tool_data.get("supports_linux", True),
                    supports_windows=tool_data.get("supports_windows", False),
                    supports_macos=tool_data.get("supports_macos", False),
                    tags=tool_data.get("tags", []),
                    is_featured=tool_data.get("is_featured", False), is_verified=True,
                )
                session.add(st)
            await session.commit()
            logger.info(f"Seeded {len(TOOL_CATALOG)} tools into store catalog")
    
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")
    yield
    
    # Shutdown
    logger.info("Shutting down gracefully...")
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional Cross-Platform CLI Tool Management Platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)


# ─── Middleware Stack ─────────────────────────────────────────────────────────

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Remove server identification
    response.headers.pop("server", None)
    
    return response


# Request Logging Middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log request details and timing."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Log slow requests
    if duration > 5.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {duration:.2f}s (status={response.status_code})"
        )
    elif settings.DEBUG:
        logger.debug(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )
    
    # Add timing header
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response


# CORS - configured from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Response-Time"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Trusted Host (production only)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )


# ─── Global Exception Handler ────────────────────────────────────────────────

# Register structured exception handlers
register_exception_handlers(app)


# ─── Routes ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(tools.router)
app.include_router(execution.router)
app.include_router(system.router)
app.include_router(store.router)
app.include_router(workflows.router)


# ─── WebSocket Endpoint ──────────────────────────────────────────────────────

@app.websocket("/ws/terminal/{execution_id}")
async def websocket_terminal(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time terminal output streaming."""
    # Authenticate via query param token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return
    
    try:
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await ws_manager.connect(websocket, execution_id, user_id)
    
    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, execution_id, user_id)
    except Exception:
        ws_manager.disconnect(websocket, execution_id, user_id)


# ─── Root & Health ────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint - basic service info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        access_log=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
