"""Checks on data/ that run in CI. Run: python scripts/validate.py"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
failed = 0


def check(ok: bool, msg: str) -> None:
    global failed
    print(("ok    " if ok else "FAIL  ") + msg)
    failed += not ok


p = pd.read_csv(D / "palavras.csv", keep_default_na=False)
lv = pd.read_csv(D / "livros.csv")
pb = pd.read_csv(D / "palavras_por_livro.csv", keep_default_na=False)
car = pd.read_csv(D / "palavras_caracteristicas.csv", keep_default_na=False)
ctx = pd.read_csv(D / "contextos.csv", keep_default_na=False)
st = json.loads((D / "stats.json").read_text(encoding="utf-8"))

check(p.palavra.is_unique, "palavras: one row per word")
check((p.ocorrencias == p.ocorrencias_at + p.ocorrencias_nt).all(), "palavras: occurrences = OT + NT")
check((p.versiculos <= p.ocorrencias).all() and (p.capitulos <= p.versiculos).all() and (p.livros <= p.capitulos).all(),
      "palavras: books <= chapters <= verses <= occurrences")
check(p.palavra.str.len().ge(2).all(), "palavras: words have 2+ letters")
check(int(p.ocorrencias.sum()) == st["palavras"] and len(p) == st["vocabulario"], "palavras: totals match stats.json")
check(len(lv) == 66 and lv.livro.is_unique and (lv.ordem == range(1, 67)).all(), "livros: 66 books, in order")
check(set(lv.testamento) == {"AT", "NT"} and (lv.testamento == "AT").sum() == 39, "livros: 39 in the OT, 27 in the NT")
check(int(lv.palavras.sum()) == st["palavras"] and int(lv.versiculos.sum()) == st["versiculos"], "livros: totals match")
check(set(pb.livro) == set(lv.livro), "palavras_por_livro: every book")
tot = pb.groupby("palavra").ocorrencias.sum()
check(tot.reindex(p.palavra).fillna(0).astype(int).tolist() == p.ocorrencias.tolist(), "palavras_por_livro: sums to palavras")
check(not car.palavra.isin(p[p.funcional].palavra).any(), "palavras_caracteristicas: no function words")
check(set(car.livro) <= set(lv.livro), "palavras_caracteristicas: known books")
# excerpts are short quotations, never whole verses at length
n_words = ctx.trecho.str.replace("…", "", regex=False).str.split().str.len()
check((n_words <= 13).all(), "contextos: at most 13 words per excerpt")
check(ctx.groupby("palavra").size().max() <= 3, "contextos: at most 3 excerpts per word")
check(ctx.palavra.nunique() <= 60, "contextos: at most 60 words with excerpts")

print(f"{failed} check(s) failed" if failed else "all checks passed")
sys.exit(1 if failed else 0)
