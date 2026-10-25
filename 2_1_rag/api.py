import json
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent import stream_turn

app = FastAPI(title="Accidentes RAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatIn(BaseModel):
    pregunta: str = Field(min_length=1)
    thread_id: str | None = None


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    thread_id = body.thread_id or str(uuid.uuid4())

    async def events():
        yield _sse({"type": "thread", "thread_id": thread_id})
        async for event in stream_turn(body.pregunta, thread_id):
            yield _sse(event)
        yield _sse({"type": "done"})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
