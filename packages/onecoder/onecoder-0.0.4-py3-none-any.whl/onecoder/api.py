import json
import asyncio
import os
from typing import Any
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from .sessions import DurableSessionService
from google.genai.types import Content, Part
from .ipc_auth import TOKEN_STORE
from .agent import get_root_agent
from .distillation import capture_engine

app = FastAPI(title="OneCoder Agent API")

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for web UI
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup ADK session service and runner
session_service = DurableSessionService()
runner = Runner(
    session_service=session_service, agent=get_root_agent(), app_name="onecoder-unified-api"
)


@app.get("/")
async def root(token: str | None = None):
    """Root endpoint - redirects to web UI if token provided."""
    if token:
        return RedirectResponse(url=f"/static/index.html?token={token}")
    return {
        "message": "OneCoder API",
        "version": "0.1.0",
        "endpoints": {
            "web_ui": "/static/index.html?token=<token>",
            "chat": "POST /chat",
            "stream": "GET /stream",
        },
    }


async def verify_token(request: Request):
    """
    Middleware-like dependency to verify session-based tokens.
    The token can be passed in 'Authorization: Bearer <token>' or '?token=<token>'.
    """
    token = request.query_params.get("token")
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token or not TOKEN_STORE.validate_token(token):
        raise HTTPException(
            status_code=401, detail="Unauthorized: Invalid or expired token"
        )


@app.post("/chat")
async def chat(user_id: str, session_id: str, message: str, _=Depends(verify_token)):
    """
    Standard synchronous chat endpoint (returns full response).
    """
    session = await session_service.get_session(
        app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=Content(parts=[Part(text=message)], role="user"),
    ):
        if hasattr(event, "content") and event.content and event.content.parts:
            text_part = next((part for part in event.content.parts if part.text), None)
            if text_part and text_part.text:
                final_text += text_part.text

    return {"response": final_text}


@app.get("/stream")
async def stream(user_id: str, session_id: str, message: str, token: str):
    """
    SSE endpoint for streaming agent responses and events.
    FastAPI handles StreamingResponse well for this.
    Note: Token validation is done inside since SSE doesn't always support headers easily.
    """
    if not TOKEN_STORE.validate_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = await session_service.get_session(
        app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name="onecoder-unified-api", user_id=user_id, session_id=session_id
        )

    async def event_generator():
        capture_engine.start_session(session_id)
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=Content(parts=[Part(text=message)], role="user"),
            ):
                # Format event for SSE
                event_data: dict[str, str | dict[str, Any] | None] = {
                    "type": type(event).__name__,
                }

                if hasattr(event, "content") and event.content and event.content.parts:
                    text_part = next(
                        (part for part in event.content.parts if part.text), None
                    )
                    if text_part and text_part.text:
                        event_data["text"] = text_part.text

                    # Capture tool calls or delegation events if present
                    tool_call = next(
                        (part for part in event.content.parts if part.function_call),
                        None,
                    )
                    if tool_call and tool_call.function_call:
                        event_data["tool_call"] = {
                            "name": tool_call.function_call.name,
                            "args": tool_call.function_call.args,
                        }

                capture_engine.log_event(event_data)
                yield f"data: {json.dumps(event_data)}\n\n"
            
            capture_engine.save_session()
        except Exception as e:
            yield f"data: {json.dumps({'type': 'Error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
