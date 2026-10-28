"""From the counts written by contar_palavras.py to the published files in data/.

    python scripts/build.py --raw D:\\biblia_out

Adds the `funcional` flag (function words, see stopwords.py), fixes book names, ranks the most
characteristic words of each book and writes data/stats.json. Reads and writes only counts and the short
excerpts; there is no verse text anywhere in this step.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

from stopwords import STOPWORDS

ROOT = Path(__file__).resolve().parents[1]
BOOK_FIX = {"III Joao": "III João"}


def characteristic(by_book: pd.DataFrame, top: int = 5, min_count: int = 4) -> pd.DataFrame:
    """Words a book uses far more than the rest of the Bible: log2 of the word's rate in the book over its
    rate in the other 65 books (0.5 added to both counts). Function words and words seen fewer than
    `min_count` times in the book are left out."""
    total = by_book.groupby("palavra").ocorrencias.sum()
    n_all = total.sum()
    n_book = by_book.groupby("livro").ocorrencias.sum()
    d = by_book[~by_book.palavra.isin(STOPWORDS) & (by_book.ocorrencias >= min_count)].copy()
    rest = d.palavra.map(total) - d.ocorrencias
    nb = d.livro.map(n_book)
    d["fora_do_livro"] = rest
    d["indice"] = [round(math.log2((c + 0.5) / b) - math.log2((r + 0.5) / (n_all - b)), 2)
                   for c, b, r in zip(d.ocorrencias, nb, rest)]
    d = d.sort_values(["livro", "indice"], ascending=[True, False]).groupby("livro").head(top)
    d["posicao"] = d.groupby("livro").cumcount() + 1
    return d[["livro", "posicao", "palavra", "ocorrencias", "fora_do_livro", "indice"]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    a = ap.parse_args()
    out = ROOT / "data"
    out.mkdir(exist_ok=True)

    livros = pd.read_csv(a.raw / "livros.csv").replace({"livro": BOOK_FIX})
    livros.insert(0, "ordem", range(1, len(livros) + 1))
    livros = livros.rename(columns={"posicao": "posicao_no_testamento"})
    palavras = pd.read_csv(a.raw / "palavras.csv", keep_default_na=False).replace({"primeiro_livro": BOOK_FIX})
    palavras["funcional"] = palavras.palavra.isin(STOPWORDS)
    by_book = pd.read_csv(a.raw / "palavras_por_livro.csv", keep_default_na=False).replace({"livro": BOOK_FIX})
    order = dict(zip(livros.livro, livros.ordem))
    by_book["ordem_livro"] = by_book.livro.map(order)
    by_book = by_book[["ordem_livro", "livro", "palavra", "ocorrencias"]]
    contextos = pd.read_csv(a.raw / "contextos.csv", keep_default_na=False)
    contextos["referencia"] = contextos.referencia.str.replace("III Joao", "III João", regex=False)
    car = characteristic(by_book.drop(columns="ordem_livro"))
    car.insert(0, "ordem_livro", car.livro.map(order))
    car = car.sort_values(["ordem_livro", "posicao"])

    livros.to_csv(out / "livros.csv", index=False)
    palavras.to_csv(out / "palavras.csv", index=False)
    by_book.to_csv(out / "palavras_por_livro.csv", index=False)
    car.to_csv(out / "palavras_caracteristicas.csv", index=False)
    contextos.to_csv(out / "contextos.csv", index=False)

    raw = json.loads((a.raw / "resumo.json").read_text(encoding="utf-8"))
    content = palavras[~palavras.funcional]
    stats = {
        "traducao": "Almeida Revista e Atualizada, 1993 (versao_id 1 no banco do autor)",
        "versiculos": raw["versiculos"], "livros": raw["livros"],
        "capitulos": int(livros.capitulos.sum()),
        "palavras": raw["palavras"], "vocabulario": raw["vocabulario"],
        "palavras_at": int(palavras.ocorrencias_at.sum()), "palavras_nt": int(palavras.ocorrencias_nt.sum()),
        "hapax": int((palavras.ocorrencias == 1).sum()),
        "funcionais": int(palavras.funcional.sum()),
        "ocorrencias_funcionais": int(palavras[palavras.funcional].ocorrencias.sum()),
        "top10_conteudo": content.head(10)[["palavra", "ocorrencias"]].to_dict("records"),
        "contextos": len(contextos), "palavras_com_contexto": int(contextos.palavra.nunique()),
    }
    (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "top10_conteudo"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
