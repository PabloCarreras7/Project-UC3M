import json
import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise RuntimeError("Falta ANTHROPIC_API_KEY en el entorno o en el fichero .env")

from tools import buscar_descripciones

SYSTEM_PROMPT = """Eres un agente de consulta sobre accidentes de tráfico atendidos en Madrid.
La única fuente válida son los informes recuperados con buscar_descripciones.

Llama a buscar_descripciones antes de responder.
No calcules totales ni medias: la herramienta encuentra informes parecidos, no cuenta filas.
Incluye solo incidentes que respondan a la pregunta.

Tu mensaje final es únicamente este JSON, sin markdown:
{
  "note": "una frase si hace falta aclarar algo, si no cadena vacía",
  "incidents": [
    {
      "incident": "numero_incidencia",
      "location": "distrito",
      "date": "fecha",
      "happened": "qué ocurrió, en una o dos frases"
    }
  ]
}"""

agent = create_deep_agent(
    model=ChatAnthropic(
        model="claude-opus-5-5",
        thinking={"type": "adaptive", "display": "summarized"},
        effort="medium",
        max_tokens=16000,
    ),
    tools=[buscar_descripciones],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _parts(content: object):
    if isinstance(content, str):
        if content:
            yield ("text", content)
        return
    if not isinstance(content, list):
        return
    for block in content:
        if isinstance(block, str):
            if block:
                yield ("text", block)
            continue
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind in ("thinking", "reasoning"):
            piece = block.get("thinking") or block.get("reasoning") or ""
            if piece:
                yield ("thinking", piece)
        elif kind == "text":
            piece = block.get("text") or ""
            if piece:
                yield ("text", piece)


def parse_answer(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return {"note": text, "incidents": []}
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"note": text, "incidents": []}
    incidents = []
    for row in data.get("incidents") or []:
        if not isinstance(row, dict):
            continue
        incidents.append(
            {
                "incident": str(row.get("incident") or ""),
                "location": str(row.get("location") or ""),
                "date": str(row.get("date") or ""),
                "happened": str(row.get("happened") or ""),
            }
        )
    return {"note": str(data.get("note") or ""), "incidents": incidents}


async def stream_turn(pregunta: str, thread_id: str) -> AsyncIterator[dict]:
    """Emite pensamiento, llamadas a herramientas y la respuesta final."""
    seen_thinking = ""
    answer_text = ""
    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": pregunta}]},
        config={"configurable": {"thread_id": thread_id}},
        version="v2",
    ):
        name = event.get("event")
        tool_name = event.get("name")
        if name == "on_tool_start" and tool_name == "buscar_descripciones":
            yield {"type": "tool", "status": "start"}
        elif name == "on_tool_end" and tool_name == "buscar_descripciones":
            yield {"type": "tool", "status": "end"}
        elif name == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            for kind, piece in _parts(getattr(chunk, "content", None)):
                if kind != "thinking" or not piece:
                    continue
                if piece.startswith(seen_thinking):
                    extra = piece[len(seen_thinking) :]
                    seen_thinking = piece
                else:
                    extra = piece
                    seen_thinking += piece
                if extra:
                    yield {"type": "thinking", "text": extra}
        elif name == "on_chat_model_end":
            output = event.get("data", {}).get("output")
            thinking_parts: list[str] = []
            text_parts: list[str] = []
            for kind, piece in _parts(getattr(output, "content", None)):
                if kind == "thinking":
                    thinking_parts.append(piece)
                else:
                    text_parts.append(piece)
            joined_thinking = "".join(thinking_parts)
            if joined_thinking.startswith(seen_thinking):
                extra = joined_thinking[len(seen_thinking) :]
                seen_thinking = joined_thinking
            elif joined_thinking and joined_thinking not in seen_thinking:
                extra = joined_thinking
                seen_thinking += joined_thinking
            else:
                extra = ""
            if extra:
                yield {"type": "thinking", "text": extra}
            joined_text = "".join(text_parts).strip()
            if joined_text:
                answer_text = joined_text
    yield {"type": "answer", **parse_answer(answer_text)}


def responder(pregunta: str, thread_id: str = "cli") -> str:
    """Devuelve la respuesta del agente a una pregunta."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": pregunta}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


if __name__ == "__main__":
    pregunta = " ".join(sys.argv[1:]) or input("Pregunta: ")
    print(responder(pregunta))
