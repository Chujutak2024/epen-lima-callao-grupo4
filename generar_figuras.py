"""Genera las figuras del informe a partir de los resultados agregados."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


def generate(data, output):
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.labelcolor": "#203039"})
    teal, blue = "#127366", "#254b66"
    names = ["Mayoritaria", "Logística", "Random Forest", "XGBoost"]
    scores = [data["test"][name] for name in ("Clase mayoritaria", *names[1:])]
    y = np.arange(len(names))

    fig, ax = plt.subplots(figsize=(4.5, 2.25), layout="constrained")
    ax.barh(y - .16, [r["f1_weighted"] for r in scores], .29, color=blue, label="F1 ponderado")
    ax.barh(y + .16, [r["f1_macro"] for r in scores], .29, color=teal, label="F1 macro")
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=.23)
    ax.set_xlabel("Puntaje F1")
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.0), ncol=2, frameon=False, fontsize=8)
    fig.savefig(output / "comparacion_f1.png", dpi=260)
    plt.close(fig)

    winner = max(data["test"], key=lambda name: data["test"][name]["f1_weighted"])
    cm = np.asarray(data["test"][winner]["confusion"])
    rates = cm / cm.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(4.5, 2.65), layout="constrained")
    im = ax.imshow(rates, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    fig.colorbar(im, ax=ax, fraction=.046, pad=.04, format=PercentFormatter(1), ticks=[0, .5, 1])
    short = ["Ocupado", "Desoc. abierto", "Desoc. oculto", "Inactivo pleno"]
    ax.set_yticks(range(4), short)
    ax.set_xticks(range(4), ["1", "2", "3", "4"])
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase observada")
    for i, j in np.ndindex(cm.shape):
        ax.text(j, i, f"{cm[i,j]:,}".replace(",", " "), ha="center", va="center",
                color="white" if rates[i, j] > .55 else "#182d3a")
    fig.savefig(output / "confusion_modelo_seleccionado.png", dpi=260)
    plt.close(fig)

    variables = {"C208": "Edad", "C207": "Sexo registrado", "C366": "Nivel educativo",
                 "C376": "Lengua materna", "C377": "Autoidentificación étnica",
                 "C375_5": "Comprensión o aprendizaje", "C375_6": "Relación con otras personas"}
    rows = data["importance"][:5]
    fig, ax = plt.subplots(figsize=(4.5, 2.2), layout="constrained")
    ax.barh(np.arange(len(rows)), [r["mean"] for r in rows], color=teal, height=.61,
            xerr=[r["sd"] for r in rows], error_kw={"ecolor": "#263742", "capsize": 2})
    ax.set_yticks(np.arange(len(rows)), [variables.get(r["variable"], r["variable"]) for r in rows])
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=.23)
    ax.set_axisbelow(True)
    ax.set_xlabel("Caída media del F1 ponderado")
    fig.savefig(output / "importancia_permutacion.png", dpi=260)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=Path("resultados/resultados.json"))
    parser.add_argument("--salida", type=Path, default=Path("figuras"))
    args = parser.parse_args()
    results = json.loads(args.resultados.read_text(encoding="utf-8"))
    generate(results, args.salida)
