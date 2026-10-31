"""Diagrama del pipeline de limpieza de accidentes.csv.

Las cifras salen de las salidas de data_viz/accidentes-analysis.ipynb (sección 2).
Si cambia la limpieza, actualiza STEPS y vuelve a ejecutar:

    python data_viz/diagrama_pipeline_accidentes.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "graficos_accidentes" / "00_pipeline_diagrama.png"

INK = "#1f2328"
MUTED = "#59636e"
LINE = "#c4cad1"
RAW = "#eef0f2"
STEP = "#e8f1fc"
STEP_EDGE = "#2a78d6"
OUT_FILL = "#e3f5ee"
OUT_EDGE = "#1baf7a"
USE_FILL = "#fdeee7"
USE_EDGE = "#eb6834"

# (título, detalle, cifra que cambia el paso)
STEPS = [
    ("Lectura como texto", "strip en todas las columnas; \"\" → nulo", ""),
    ("Duplicados mutuos", "100 numero_incidencia repetidos: se queda la fila más completa\n"
     "(desempate: descripción más larga); huecos rellenados con la pareja",
     "−100 filas · 3 celdas · 45 conflictos"),
    ("Categorías", "norm_key + mapas fusionados 1.2/2.1 (estado_firme 13→5 niveles,\n"
     "tipo_via 12→6, circulacion 6→4); carretera sin guion (M607)", "314 celdas"),
    ("Recuentos", "−1 en vehiculos_implicados y heridos_leves → nulo", "27 celdas"),
    ("Fecha y hora", "fecha tomada del numero_incidencia (AAAA-MM-DD);\n"
     "hora_decimal con segundos", "42 fechas corregidas"),
    ("tipo_colision inferido", "71 vacíos tras deduplicar; se rellenan desde la descripción\n"
     "(caché de Claude, caso 2.1) y se marcan en tipo_colision_inferido", "68 rellenados · 3 vacíos"),
    ("Municipio", "fuera_de_madrid marca partes de Móstoles, Alcorcón…", "50 partes"),
]

W, X0 = 7.6, 0.2          # ancho y x de las cajas de paso
BOX_H, GAP = 1.0, 0.32    # alto de caja y hueco entre cajas


def box(ax, x, y, w, h, fill, edge, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                fc=fill, ec=edge, lw=lw))


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12,
                                 color=MUTED, lw=1.2, shrinkA=0, shrinkB=0))


def main():
    n = len(STEPS)
    top = 0.95 + n * (BOX_H + GAP) + (GAP + 0.8) + (0.55 + 1.0) + 0.1
    fig, ax = plt.subplots(figsize=(9, top * 0.62))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, top)
    ax.axis("off")

    y = top - 0.95
    box(ax, X0, y, W, 0.8, RAW, LINE)
    ax.text(X0 + 0.2, y + 0.52, "Bruto · data/accidentes.csv", fontsize=11, weight="bold", color=INK)
    ax.text(X0 + 0.2, y + 0.2, "Se lee todo como texto para medir los problemas antes de tocar nada",
            fontsize=8.5, color=MUTED)
    ax.text(X0 + W - 0.2, y + 0.4, "2.062 filas × 21", fontsize=11, weight="bold",
            color=INK, ha="right", va="center")
    prev_bottom = y

    for i, (title, detail, change) in enumerate(STEPS, 1):
        y = prev_bottom - GAP - BOX_H
        arrow(ax, 4, prev_bottom, 4, y + BOX_H)
        box(ax, X0, y, W, BOX_H, STEP, STEP_EDGE)
        ax.text(X0 + 0.2, y + BOX_H - 0.24, f"{i}. {title}", fontsize=10, weight="bold", color=INK)
        ax.text(X0 + 0.2, y + BOX_H - 0.42, detail, fontsize=7.8, color=MUTED, va="top", linespacing=1.3)
        if change:
            ax.text(X0 + W - 0.2, y + BOX_H - 0.24, change, fontsize=9, weight="bold",
                    color=STEP_EDGE, ha="right")
        prev_bottom = y

    y = prev_bottom - GAP - 0.8
    arrow(ax, 4, prev_bottom, 4, y + 0.8)
    box(ax, X0, y, W, 0.8, OUT_FILL, OUT_EDGE, lw=1.6)
    ax.text(X0 + 0.2, y + 0.52, "Limpio · data_clean/accidentes_clean.csv", fontsize=11,
            weight="bold", color=INK)
    ax.text(X0 + 0.2, y + 0.2, "una fila por numero_incidencia; grave = 1 en 45 (2,29 %)",
            fontsize=8.5, color=MUTED)
    ax.text(X0 + W - 0.2, y + 0.4, "1.962 filas × 26", fontsize=11, weight="bold",
            color=INK, ha="right", va="center")
    prev_bottom = y

    uh, uw = 1.0, 3.6
    uy = prev_bottom - 0.55 - uh
    for x, title, detail in [
        (X0, "1.2 Gravedad · feature_engineering.ipynb",
         "variables + partición 80/20 estratificada\ntrain 1.569 · test 393"),
        (X0 + W - uw, "2.1 RAG · embeddings.py",
         "un documento por parte con descripción\n1.860 indexados · 102 sin texto"),
    ]:
        arrow(ax, 4, prev_bottom, x + uw / 2, uy + uh)
        box(ax, x, uy, uw, uh, USE_FILL, USE_EDGE)
        ax.text(x + 0.18, uy + uh - 0.28, title, fontsize=9, weight="bold", color=INK)
        ax.text(x + 0.18, uy + uh - 0.48, detail, fontsize=8, color=MUTED, va="top", linespacing=1.35)

    ax.set_title("Pipeline de limpieza unificada de accidentes (casos 1.2 y 2.1)",
                 fontsize=13, weight="bold", color=INK, loc="left", x=0.025)
    fig.tight_layout()
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(OUT)


if __name__ == "__main__":
    main()
