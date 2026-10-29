"""Build one word as a nested JSON record (docs/example-word.json), for the README and Kaggle.

    python scripts/make_json.py           # graça
    python scripts/make_json.py amor      # any word in data/palavras.csv

Joins the files in data/: totals from palavras.csv, the split by Testament (with the rate per 10,000
words, using the Testament sizes in stats.json), the books where the word appears most (palavras_por_livro.csv
joined to livros.csv), the books it characterises (palavras_caracteristicas.csv) and its short excerpts
(contextos.csv, at most 3, already cut to a few words). No verse text is read.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT = "graça"
TOP_BOOKS = 10
CREDIT = "Almeida Revista e Atualizada, 2ª edição, © 1993 Sociedade Bíblica do Brasil"


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, keep_default_na=False)  # "nan" is a word here, not a missing value


def per_10k(count: int, words: int) -> float:
    return round(count / words * 10_000, 2)


def build(word: str) -> dict:
    stats = json.loads((DATA / "stats.json").read_text(encoding="utf-8"))
    w = read("palavras.csv").set_index("palavra").loc[word]
    books = read("livros.csv")
    by_book = read("palavras_por_livro.csv").query("palavra == @word").merge(
        books[["ordem", "testamento", "palavras"]], left_on="ordem_livro", right_on="ordem")
    by_book = by_book.sort_values(["ocorrencias", "ordem_livro"], ascending=[False, True]).head(TOP_BOOKS)
    charac = read("palavras_caracteristicas.csv").query("palavra == @word").sort_values(["ordem_livro"])
    ctx = read("contextos.csv").query("palavra == @word")
    return {
        "palavra": word,
        "funcional": bool(w.funcional),
        "totais": {
            "ocorrencias": int(w.ocorrencias),
            "versiculos": int(w.versiculos),
            "capitulos": int(w.capitulos),
            "livros": int(w.livros),
            "primeiro_livro": w.primeiro_livro,
        },
        "por_testamento": {
            "AT": {"ocorrencias": int(w.ocorrencias_at), "por_10_mil_palavras": per_10k(w.ocorrencias_at, stats["palavras_at"])},
            "NT": {"ocorrencias": int(w.ocorrencias_nt), "por_10_mil_palavras": per_10k(w.ocorrencias_nt, stats["palavras_nt"])},
        },
        "livros_com_mais_ocorrencias": [
            {"livro": r.livro, "testamento": r.testamento, "ocorrencias": int(r.ocorrencias),
             "por_10_mil_palavras": per_10k(r.ocorrencias, r.palavras)}
            for r in by_book.itertuples()
        ],
        "caracteristica_de": [
            {"livro": r.livro, "posicao": int(r.posicao), "ocorrencias": int(r.ocorrencias),
             "fora_do_livro": int(r.fora_do_livro), "indice": float(r.indice)}
            for r in charac.itertuples()
        ],
        "contextos": [{"referencia": r.referencia, "trecho": r.trecho} for r in ctx.head(3).itertuples()],
        "traducao": CREDIT,
    }


def main() -> None:
    word = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    out = ROOT / "docs" / "example-word.json"
    out.write_text(json.dumps(build(word), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
