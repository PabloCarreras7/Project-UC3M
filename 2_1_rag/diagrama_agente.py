"""Diagrama del agente RAG actual (agent.py, tools.py, api.py).

La estructura del grafo es la que devuelve agent.get_graph() con deepagents 0.7:
__start__ -> PatchToolCallsMiddleware.before_agent -> model <-> tools -> __end__.
Si cambia el agente, actualiza el diagrama y vuelve a ejecutar:

    python 2_1_rag/diagrama_agente.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figuras" / "agente_langgraph.png"

INK = "#1f2328"
MUTED = "#59636e"
LINE = "#c4cad1"
GRAPH_FILL, GRAPH_EDGE = "#e8f1fc", "#2a78d6"
TOOL_FILL, TOOL_EDGE = "#fdeee7", "#eb6834"
DATA_FILL, DATA_EDGE = "#e3f5ee", "#1baf7a"
IO_FILL = "#eef0f2"


def box(ax, x, y, w, h, title, detail="", fill=IO_FILL, edge=LINE, lw=1.3, round_=0.12, title_size=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={round_}",
                                fc=fill, ec=edge, lw=lw))
    if detail:
        ax.text(x + w / 2, y + h - 0.26, title, ha="center", va="center", fontsize=title_size,
                weight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.46, detail, ha="center", va="top", fontsize=7.8,
                color=MUTED, linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=title_size,
                weight="bold", color=INK)


def arrow(ax, a, b, text="", dashed=False, rad=0.0, text_xy=None, color=MUTED):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, color=color, lw=1.3,
                                 linestyle=(0, (4, 3)) if dashed else "-",
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if text:
        x, y = text_xy or ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        ax.text(x, y, text, fontsize=7.8, color=MUTED, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=1.2))


def main():
    fig, ax = plt.subplots(figsize=(11, 8.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.6)
    ax.axis("off")

    # Entrada
    box(ax, 0.3, 7.35, 2.9, 0.8, "Frontend React", "POST /chat · pregunta + thread_id")
    box(ax, 3.9, 7.35, 3.1, 0.8, "FastAPI · api.py", "stream_turn() → eventos SSE")
    arrow(ax, (3.2, 7.75), (3.9, 7.75))

    # Grafo LangGraph (incluye el nodo tools)
    ax.add_patch(FancyBboxPatch((0.3, 2.75), 10.4, 4.15, boxstyle="round,pad=0,rounding_size=0.15",
                                fc="white", ec=GRAPH_EDGE, lw=1.2, linestyle=(0, (5, 3))))
    ax.text(0.5, 6.62, "Grafo LangGraph · create_deep_agent (deepagents)", fontsize=10.5,
            weight="bold", color=GRAPH_EDGE)
    ax.text(0.5, 6.36, "checkpointer MemorySaver: el historial se guarda por thread_id",
            fontsize=7.8, color=MUTED)

    box(ax, 2.55, 5.7, 2.2, 0.45, "__start__", fill="white", edge=LINE, round_=0.22)
    box(ax, 1.75, 4.85, 3.8, 0.65, "PatchToolCalls · before_agent",
        "repara llamadas a herramientas sin respuesta", fill=GRAPH_FILL, edge=GRAPH_EDGE)
    box(ax, 1.75, 3.55, 3.8, 1.1, "model", "Claude Opus 5.5 · adaptive thinking, effort medium\n"
        "system prompt: buscar antes de responder,\nno contar filas, responder en JSON",
        fill=GRAPH_FILL, edge=GRAPH_EDGE, lw=1.8, title_size=11)
    box(ax, 2.55, 2.9, 2.2, 0.42, "__end__", fill="#d8d2fd", edge=LINE, round_=0.2)

    arrow(ax, (5.45, 7.35), (4.75, 5.95))
    arrow(ax, (3.65, 5.7), (3.65, 5.5))
    arrow(ax, (3.65, 4.85), (3.65, 4.65))
    arrow(ax, (3.65, 3.55), (3.65, 3.32), dashed=True)
    ax.text(3.85, 3.44, "sin más llamadas", fontsize=7.5, color=MUTED, va="center")
    arrow(ax, (1.75, 3.8), (1.75, 4.4), dashed=True, rad=-1.6)
    ax.text(0.4, 4.1, "salto de\nmiddleware", fontsize=7.2, color=MUTED, va="center")

    box(ax, 7.4, 3.55, 3.1, 1.6, "tools", "buscar_descripciones(pregunta, k=5)\n"
        "+ herramientas de deepagents\n(ficheros, task)", fill=TOOL_FILL, edge=TOOL_EDGE, lw=1.6,
        title_size=11)
    arrow(ax, (5.55, 4.4), (7.4, 4.75), text="tool call", dashed=True, text_xy=(6.47, 4.85))
    arrow(ax, (7.4, 3.85), (5.55, 3.85), text="informes", dashed=True, text_xy=(6.47, 3.72))

    # Recuperación (fuera del grafo)
    box(ax, 7.4, 1.45, 3.1, 1.05, "Pinecone", "índice accidentes-descripcion · 1.860 descripciones\n"
        "Qwen3-Embedding-0.6B (1024 d)", fill=DATA_FILL, edge=DATA_EDGE)
    arrow(ax, (8.95, 3.55), (8.95, 2.5), text="similarity_search top-5", text_xy=(8.95, 3.0))
    box(ax, 7.4, 0.1, 3.1, 0.95, "data_clean/accidentes_clean.csv",
        "embeddings.py: un documento por parte\nmetadatos: numero_incidencia, distrito, fecha",
        fill="white", edge=DATA_EDGE, title_size=8.8)
    arrow(ax, (8.95, 1.05), (8.95, 1.45), text="indexación", text_xy=(9.65, 1.25))

    # Salida
    box(ax, 0.3, 0.6, 6.7, 1.15, "Respuesta · parse_answer()",
        "JSON {note, incidents: [incident, location, date, happened]}\n"
        "el frontend muestra el razonamiento, la llamada a la herramienta y la tabla de incidentes",
        fill=IO_FILL, edge=LINE)
    arrow(ax, (3.65, 2.9), (3.65, 1.75))

    ax.set_title("Agente RAG actual (2_1_rag/agent.py)", fontsize=13, weight="bold", color=INK,
                 loc="left", x=0.02)
    fig.tight_layout()
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(OUT)


if __name__ == "__main__":
    main()
