"""
VIGIL LABS - Main Application
FastAPI application entry point with full CORS, WebSocket, and lifecycle management.
"""
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, close_db, AsyncSessionLocal
from app.core.security import decode_token
from app.api.routes import auth, tools, execution, system, store, workflows
from app.api.websocket.terminal import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
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
                    github_repo=tool_data.get("github_repo"),
                    github_url=tool_data.get("github_url"),
                    risk_level=tool_data.get("risk_level", "medium"),
                    supports_linux=tool_data.get("supports_linux", True),
                    supports_windows=tool_data.get("supports_windows", False),
                    tags=tool_data.get("tags", []),
                    is_featured=tool_data.get("is_featured", False), is_verified=True,
                )
                session.add(st)
            await session.commit()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional Cross-Platform CLI Tool Management Platform",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "app://./"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(tools.router)
app.include_router(execution.router)
app.include_router(system.router)
app.include_router(store.router)
app.include_router(workflows.router)


# WebSocket endpoint for terminal streaming
@app.websocket("/ws/terminal/{execution_id}")
async def websocket_terminal(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time terminal output."""
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


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
