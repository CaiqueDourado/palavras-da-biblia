"""Cover image (EN and PT): the three things in the dataset, each with real values. Run: python scripts/make_cover.py"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, LINE, BG, CARD = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff"
AT, NT, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
NAMES = {"senhor": "Senhor", "deus": "Deus", "israel": "Israel", "jesus": "Jesus", "davi": "Davi"}
BOOKS = ["Rute", "Provérbios", "Joel", "Daniel", "Atos", "Apocalipse"]
QUOTES = [("luz", "Gênesis 1:3"), ("preguiçoso", "Provérbios 6:6"), ("fé", "Habacuque 2:4")]
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

T = {
    "": dict(title="The words of the Bible", sub="{palavras} words · {vocab} distinct · 66 books · counts of the Almeida Revista e Atualizada (1993)",
             p1="Most frequent", p1s="function words left out", p2="One word per book", p2s="used far more than in the rest",
             p3="In context", p3s="short excerpts, cut at both ends", foot="palavras-da-biblia · counts per word, per book and per Testament"),
    ".pt-BR": dict(title="As palavras da Bíblia", sub="{palavras} palavras · {vocab} diferentes · 66 livros · contagens da Almeida Revista e Atualizada (1993)",
                   p1="Mais frequentes", p1s="sem palavras funcionais", p2="Uma palavra por livro", p2s="usada muito mais que no resto",
                   p3="No contexto", p3s="trechos curtos, cortados nas pontas", foot="palavras-da-biblia · contagens por palavra, por livro e por Testamento"),
}


def num(n, pt):
    s = f"{n:,}"
    return s.replace(",", ".") if pt else s


def panel(ax, x, w, color, title, sub):
    ax.add_patch(FancyBboxPatch((x, 6), w, 52, boxstyle="round,pad=0,rounding_size=1.4", fc=CARD, ec=LINE, lw=1.1))
    ax.add_patch(FancyBboxPatch((x, 57.2), w, 0.8, boxstyle="square,pad=0", fc=color, ec="none"))
    ax.text(x + 2, 53, title, fontsize=13, weight="bold", color=INK, va="center")
    ax.text(x + 2, 49.2, sub, fontsize=8.6, color=MUTED, va="center")


def main() -> None:
    d = ROOT / "data"
    p = pd.read_csv(d / "palavras.csv", keep_default_na=False)
    car = pd.read_csv(d / "palavras_caracteristicas.csv", keep_default_na=False)
    ctx = pd.read_csv(d / "contextos.csv", keep_default_na=False)
    stats = json.loads((d / "stats.json").read_text(encoding="utf-8"))
    top = p[~p.funcional].head(8)
    first = car[car.posicao == 1].set_index("livro").palavra
    for suf, t in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(12, 6.2), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 120)
        ax.set_ylim(0, 74)
        ax.axis("off")
        ax.text(3, 69, t["title"], fontsize=21, weight="bold", color=INK, va="center")
        ax.text(3, 63.6, t["sub"].format(palavras=num(stats["palavras"], pt), vocab=num(stats["vocabulario"], pt)),
                fontsize=10.5, color=MUTED, va="center")

        x1, w = 3, 36
        panel(ax, x1, w, AT, t["p1"], t["p1s"])
        mx = top.ocorrencias.max()
        for i, r in enumerate(top.itertuples()):
            y = 43 - i * 4.4
            ax.text(x1 + 2, y, NAMES.get(r.palavra, r.palavra), fontsize=9.4, color=INK, va="center")
            bw = 18 * r.ocorrencias / mx
            at_w = bw * r.ocorrencias_at / r.ocorrencias
            ax.add_patch(FancyBboxPatch((x1 + 11, y - 1.2), at_w, 2.4, boxstyle="square,pad=0", fc=AT, ec="none"))
            ax.add_patch(FancyBboxPatch((x1 + 11 + at_w, y - 1.2), bw - at_w, 2.4, boxstyle="square,pad=0", fc=NT, ec="none"))
            ax.text(x1 + 11.6 + bw, y, num(int(r.ocorrencias), pt), fontsize=8.2, color=MUTED, va="center")

        x2 = x1 + w + 2.5
        panel(ax, x2, w, AQUA, t["p2"], t["p2s"])
        for i, b in enumerate(BOOKS):
            c, r = i % 2, i // 2
            bx, by = x2 + 2 + c * 16.5, 35.5 - r * 11.5
            ax.add_patch(FancyBboxPatch((bx, by), 15.5, 9.5, boxstyle="round,pad=0,rounding_size=0.8", fc=BG, ec=LINE, lw=0.8))
            ax.text(bx + 1.2, by + 6.8, b, fontsize=7.8, color=MUTED, va="center")
            ax.text(bx + 1.2, by + 2.8, first[b], fontsize=11, weight="bold", color=INK, va="center")

        x3 = x2 + w + 2.5
        w3 = 117 - x3
        panel(ax, x3, w3, NT, t["p3"], t["p3s"])
        for i, (word, ref) in enumerate(QUOTES):
            row = ctx[(ctx.palavra == word) & (ctx.referencia == ref)].iloc[0]
            y = 41 - i * 12
            ax.text(x3 + 2, y, row.referencia, fontsize=8.4, color=MUTED, va="center")
            trecho = row.trecho if len(row.trecho) <= 44 else row.trecho[:43].rsplit(" ", 1)[0] + " …"
            ax.text(x3 + 2, y - 4, f"“{trecho}”", fontsize=9.2, color=INK, va="center", style="italic")

        ax.text(3, 2.6, t["foot"], fontsize=8.4, color=MUTED)
        ax.text(117, 2.6, "github.com/CaiqueDourado", fontsize=8.4, color=MUTED, ha="right")
        fig.savefig(ROOT / "docs" / "img" / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    main()
