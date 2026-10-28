"""Figures of the study, EN and PT, from data/. Run: python scripts/make_figures.py"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
INK, MUTED, GRID, BG = "#111111", "#5c5c5c", "#e6e8eb", "#fdfdfc"
AT, NT = "#2a78d6", "#eb6834"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

T = {
    "": dict(
        top_t="The 25 most frequent words of the Bible", top_s="Almeida Revista e Atualizada (1993), function words left out",
        at="Old Testament", nt="New Testament",
        diff_t="Words of one Testament", diff_s="Occurrences per 10,000 words of each Testament, words seen 80+ times; (0) = never in the other Testament",
        diff_l="more in the Old Testament", diff_r="more in the New Testament",
        books_t="How long each book is", books_s="Words per book, in canonical order",
        zipf_t="A few words do most of the work", zipf_s="Occurrences by rank, log scale (Zipf's law)",
        zipf_a="309 function words\n(de, que, os, do, para…)\nare 48.9% of all words", zipf_b="13,268 words\nappear only once",
        rank="rank of the word", occ="occurrences",
        grid_t="One word per book", grid_s="The word each book uses most more than the rest of the Bible (function words left out)",
        src="Source: palavras-da-biblia, counts of the Almeida Revista e Atualizada (1993)"),
    ".pt-BR": dict(
        top_t="As 25 palavras que mais aparecem na Bíblia", top_s="Almeida Revista e Atualizada (1993), sem palavras funcionais",
        at="Antigo Testamento", nt="Novo Testamento",
        diff_t="Palavras de um Testamento só", diff_s="Ocorrências a cada 10 mil palavras de cada Testamento, palavras com 80+ ocorrências; (0) = nunca no outro Testamento",
        diff_l="mais no Antigo Testamento", diff_r="mais no Novo Testamento",
        books_t="O tamanho de cada livro", books_s="Palavras por livro, na ordem canônica",
        zipf_t="Poucas palavras fazem quase todo o trabalho", zipf_s="Ocorrências por posição, escala logarítmica (lei de Zipf)",
        zipf_a="309 palavras funcionais\n(de, que, os, do, para…)\nsão 48,9% de todas as palavras", zipf_b="13.268 palavras\naparecem uma vez só",
        rank="posição da palavra", occ="ocorrências",
        grid_t="Uma palavra por livro", grid_s="A palavra que cada livro usa muito mais que o resto da Bíblia (sem palavras funcionais)",
        src="Fonte: palavras-da-biblia, contagens da Almeida Revista e Atualizada (1993)"),
}


def style(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)


def head(fig, t, s, src):
    fig.text(0.02, 0.965, t, fontsize=16, weight="bold", color=INK, va="top")
    fig.text(0.02, 0.905, s, fontsize=10, color=MUTED, va="top")
    fig.text(0.02, 0.015, src, fontsize=8, color=MUTED)


def num(n, pt):
    s = f"{n:,}"
    return s.replace(",", ".") if pt else s


def top_words(p, t, suf):
    pt = suf == ".pt-BR"
    d = p[~p.funcional].head(25).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 8.2), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.14, right=0.93, top=0.84, bottom=0.08)
    y = range(len(d))
    ax.barh(y, d.ocorrencias_at, color=AT, height=0.72, edgecolor=BG, linewidth=1)
    ax.barh(y, d.ocorrencias_nt, left=d.ocorrencias_at, color=NT, height=0.72, edgecolor=BG, linewidth=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels([w.capitalize() if w in ("senhor", "deus", "israel", "jesus", "davi", "moisés", "judá",
                                                 "jerusalém", "egito", "cristo") else w for w in d.palavra],
                       fontsize=10, color=INK)
    for yi, total in zip(y, d.ocorrencias):
        ax.text(total + 60, yi, num(total, pt), va="center", fontsize=8.5, color=MUTED)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    style(ax)
    ax.legend([t["at"], t["nt"]], loc="lower right", frameon=False, fontsize=9)
    head(fig, t["top_t"], t["top_s"], t["src"])
    fig.savefig(OUT / f"top-words{suf}.png", facecolor=BG)
    plt.close(fig)


def at_vs_nt(p, stats, t, suf):
    at_n, nt_n = stats["palavras_at"], stats["palavras_nt"]
    d = p[~p.funcional & (p.ocorrencias >= 80)].copy()
    d["r_at"] = d.ocorrencias_at / at_n * 1e4
    d["r_nt"] = d.ocorrencias_nt / nt_n * 1e4
    d["lr"] = [math.log2((n + 1) / nt_n) - math.log2((a + 1) / at_n) for a, n in zip(d.ocorrencias_at, d.ocorrencias_nt)]
    left = d.sort_values("lr").head(12)
    right = d.sort_values("lr", ascending=False).head(12)
    fig, axes = plt.subplots(1, 2, figsize=(10, 6.6), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.8, bottom=0.08, wspace=0.55)
    for ax, sub, col, rate, title in ((axes[0], left, AT, "r_at", t["diff_l"]), (axes[1], right, NT, "r_nt", t["diff_r"])):
        sub = sub.sort_values(rate)
        ax.barh(range(len(sub)), sub[rate], color=col, height=0.7)
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels(sub.palavra, fontsize=10, color=INK)
        for i, (r, a, n) in enumerate(zip(sub[rate], sub.ocorrencias_at, sub.ocorrencias_nt)):
            other = n if col == AT else a
            val = f"{r:.1f}".replace(".", ",") if suf else f"{r:.1f}"
            ax.text(r + sub[rate].max() * 0.02, i, val + ("" if other else "  (0)"), va="center", fontsize=8, color=MUTED)
        ax.set_title(title, loc="left", fontsize=11, color=col, weight="bold")
        ax.set_xlim(0, sub[rate].max() * 1.3)
        style(ax)
    head(fig, t["diff_t"], t["diff_s"], t["src"])
    fig.savefig(OUT / f"at-vs-nt{suf}.png", facecolor=BG)
    plt.close(fig)


def books(lv, t, suf):
    pt = suf == ".pt-BR"
    fig, ax = plt.subplots(figsize=(12, 5.9), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.82, bottom=0.33)
    cols = [AT if x == "AT" else NT for x in lv.testamento]
    ax.bar(range(len(lv)), lv.palavras, color=cols, width=0.78)
    ax.set_xticks(range(len(lv)))
    ax.set_xticklabels(lv.livro, rotation=90, fontsize=7.4, color=INK)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    style(ax)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: num(int(v), pt)))
    for name in ("Salmos", "Jeremias", "II João"):
        i = lv.index[lv.livro == name][0]
        ax.text(i, lv.palavras[i] + 500, num(int(lv.palavras[i]), pt), ha="center", fontsize=8, color=INK)
    ax.legend(handles=[matplotlib.patches.Patch(color=AT, label=t["at"]), matplotlib.patches.Patch(color=NT, label=t["nt"])],
              loc="upper right", frameon=False, fontsize=9)
    head(fig, t["books_t"], t["books_s"], t["src"])
    fig.savefig(OUT / f"books{suf}.png", facecolor=BG)
    plt.close(fig)


def zipf(p, t, suf):
    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=110)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.82, bottom=0.12)
    r = range(1, len(p) + 1)
    ax.loglog(r, p.ocorrencias, color=AT, lw=2)
    ax.set_xlabel(t["rank"], color=MUTED, fontsize=9)
    ax.set_ylabel(t["occ"], color=MUTED, fontsize=9)
    ax.grid(True, which="major", color=GRID, lw=0.8)
    style(ax)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(GRID)
    ax.text(12, 120, t["zipf_a"], fontsize=9, color=INK)
    first_once = int((p.ocorrencias > 1).sum()) + 1
    ax.annotate(t["zipf_b"], (first_once, 1), xytext=(first_once / 30, 3.2), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    head(fig, t["zipf_t"], t["zipf_s"], t["src"])
    fig.savefig(OUT / f"zipf{suf}.png", facecolor=BG)
    plt.close(fig)


def grid(lv, car, t, suf):
    first = car[car.posicao == 1].set_index("livro")
    cols, rows = 6, 11
    fig = plt.figure(figsize=(12, 10.4), dpi=110)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.02, 0.04, 0.96, 0.84])
    ax.set_xlim(0, cols)
    ax.set_ylim(rows, 0)
    ax.axis("off")
    for i, b in enumerate(lv.itertuples()):
        c, r = i % cols, i // cols
        col = AT if b.testamento == "AT" else NT
        ax.add_patch(matplotlib.patches.FancyBboxPatch((c + 0.04, r + 0.06), 0.92, 0.86,
                     boxstyle="round,pad=0,rounding_size=0.06", fc="white", ec=GRID, lw=0.9))
        ax.add_patch(matplotlib.patches.Rectangle((c + 0.04, r + 0.06), 0.03, 0.86, fc=col, ec="none"))
        ax.text(c + 0.14, r + 0.3, b.livro, fontsize=7.6, color=MUTED, va="center")
        w = first.palavra.get(b.livro, "")
        ax.text(c + 0.14, r + 0.62, w, fontsize=11 if len(w) < 14 else 9, color=INK, weight="bold", va="center")
    head(fig, t["grid_t"], t["grid_s"], t["src"])
    fig.savefig(OUT / f"one-word-per-book{suf}.png", facecolor=BG)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    import json
    p = pd.read_csv(ROOT / "data" / "palavras.csv", keep_default_na=False)
    lv = pd.read_csv(ROOT / "data" / "livros.csv")
    car = pd.read_csv(ROOT / "data" / "palavras_caracteristicas.csv", keep_default_na=False)
    stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    for suf, t in T.items():
        top_words(p, t, suf)
        at_vs_nt(p, stats, t, suf)
        books(lv, t, suf)
        zipf(p, t, suf)
        grid(lv, car, t, suf)
    print("figures in", OUT)


if __name__ == "__main__":
    main()
