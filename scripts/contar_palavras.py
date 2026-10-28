"""Count the words of the Bible in the author's SQL Server, and write ONLY the counts.

    python -m pip install --user pyodbc
    python contar_palavras.py --server localhost --out D:\\biblia_out
    python contar_palavras.py --server localhost --schema       # only list the tables and columns

The verse text (Almeida Revista e Atualizada, 1993, a protected translation) is read here, on the author's
machine, and never written: the outputs are word counts per word, per book and per testament.

Outputs in --out:
  palavras.csv            word, occurrences, verses, chapters, books, occurrences in OT and NT, first book
  palavras_por_livro.csv  book × word occurrences (only pairs with at least one)
  livros.csv              book, testament, position, chapters, verses, words, distinct words
  contextos.csv           short excerpts for the study: up to 3 per word, for the words of the study
                          (--palavras), cut at both ends (at most 4 words on each side), with the reference
  resumo.json             totals and the query used

The excerpts are quotations for a study (with the source named), not the text: a handful of words, a few
words of context each. The full verses are never written.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

VERSION_ID = 1  # 1993 - Almeida Revista e Atualizada, the version the site used (ver_vrs_id = 1)

QUERY = """
SELECT t.tes_nome, l.liv_posicao, l.liv_nome, v.ver_capitulo, v.ver_versiculo, v.ver_texto
FROM biblia.dbo.versiculos v
JOIN biblia.dbo.livros l ON l.liv_id = v.ver_liv_id
JOIN biblia.dbo.testamentos t ON t.tes_id = l.liv_tes_id
WHERE v.ver_vrs_id = ?
ORDER BY t.tes_id, l.liv_posicao, v.ver_capitulo, v.ver_versiculo
"""

# words shown in the study (README and notebook), with up to 3 short excerpts each
STUDY_WORDS = ("senhor deus terra israel rei povo coração jesus cristo fé graça amor paz luz vida morte "
               "espírito verdade justiça pecado glória sangue pão água besta noemi preguiçoso filhinhos "
               "gafanhoto peixe louvai-o mordecai sansão gideão melquisedeque nicodemos joio saulo").split()

TOKENS = re.compile(r"\S+")
WORD = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)
TAG = re.compile(r"<[^>]+>")


def words(text: str) -> list[str]:
    """Lower-case words with accents kept; hyphenated forms stay one word (ouvi-o); 1-letter words dropped,
    as the site did (len(palavra) >= 2)."""
    text = unicodedata.normalize("NFC", TAG.sub(" ", text or "")).lower()
    return [w for w in WORD.findall(text) if len(w) >= 2]


def connect(server: str):
    import pyodbc
    return pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Trusted_Connection=yes",
                          autocommit=True)


def show_schema(cur) -> None:
    for table in ("versiculos", "livros", "testamentos", "versoes", "versiculos_palavras"):
        cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM biblia.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? "
                    "ORDER BY ORDINAL_POSITION", table)
        print(table, [f"{c} {t}" for c, t in cur.fetchall()])
    cur.execute("SELECT * FROM biblia.dbo.versoes")
    print("versoes", cur.fetchall())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="localhost")
    ap.add_argument("--out", type=Path, default=Path("biblia_out"))
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--palavras", default=",".join(STUDY_WORDS),
                    help="comma-separated words that get excerpts (default: the words of the study)")
    ap.add_argument("--janela", type=int, default=4, help="words kept on each side (default 4, max 6)")
    a = ap.parse_args()
    a.janela = min(a.janela, 6)
    cur = connect(a.server).cursor()
    if a.schema:
        show_schema(cur)
        return
    try:
        cur.execute(QUERY, VERSION_ID)
    except Exception as e:  # noqa: BLE001
        print(f"The query failed ({e}). Run with --schema and send the output, so the joins can be fixed.")
        raise SystemExit(1)

    occ, occ_ot, occ_nt = Counter(), Counter(), Counter()
    verses, chapters, books = defaultdict(set), defaultdict(set), defaultdict(set)
    first_book: dict[str, str] = {}
    by_book: dict[str, Counter] = defaultdict(Counter)
    book_info: dict[str, dict] = {}
    n_verses = 0
    tokens_by_ref: dict[tuple, list[str]] = {}
    for testament, pos, book, chap, vers, text in cur:
        n_verses += 1
        ot = "Antigo" in (testament or "")
        info = book_info.setdefault(book, {"livro": book, "testamento": "AT" if ot else "NT", "posicao": pos,
                                           "capitulos": set(), "versiculos": 0, "palavras": 0})
        info["capitulos"].add(chap)
        info["versiculos"] += 1
        ws = words(text)
        tokens_by_ref[(book, chap, vers)] = TOKENS.findall(unicodedata.normalize("NFC", TAG.sub(" ", text or "")))
        info["palavras"] += len(ws)
        for w in ws:
            occ[w] += 1
            (occ_ot if ot else occ_nt)[w] += 1
            verses[w].add((book, chap, vers))
            chapters[w].add((book, chap))
            books[w].add(book)
            first_book.setdefault(w, book)
            by_book[book][w] += 1

    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / "palavras.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["palavra", "ocorrencias", "versiculos", "capitulos", "livros", "ocorrencias_at",
                     "ocorrencias_nt", "primeiro_livro"])
        for w, n in sorted(occ.items(), key=lambda kv: (-kv[1], kv[0])):
            wr.writerow([w, n, len(verses[w]), len(chapters[w]), len(books[w]), occ_ot[w], occ_nt[w], first_book[w]])
    with open(a.out / "palavras_por_livro.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["livro", "palavra", "ocorrencias"])
        for book in sorted(by_book, key=lambda b: (book_info[b]["testamento"] != "AT", book_info[b]["posicao"])):
            for w, n in sorted(by_book[book].items(), key=lambda kv: (-kv[1], kv[0])):
                wr.writerow([book, w, n])
    with open(a.out / "livros.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["posicao", "livro", "testamento", "capitulos", "versiculos", "palavras", "vocabulario"])
        for b in sorted(book_info.values(), key=lambda i: (i["testamento"] != "AT", i["posicao"])):
            wr.writerow([b["posicao"], b["livro"], b["testamento"], len(b["capitulos"]), b["versiculos"],
                         b["palavras"], len(by_book[b["livro"]])])
    chosen = [w for w in a.palavras.split(",") if w in occ]
    with open(a.out / "contextos.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["palavra", "referencia", "trecho"])
        for w in chosen:
            refs = sorted(verses[w], key=lambda r: (book_info[r[0]]["testamento"] != "AT", book_info[r[0]]["posicao"], r[1], r[2]))
            step = max(1, len(refs) // 3)
            for ref in refs[::step][:3]:
                toks = tokens_by_ref[ref]
                low = [words(t)[0] if words(t) else "" for t in toks]
                i = low.index(w) if w in low else 0
                lo, hi = max(0, i - a.janela), min(len(toks), i + a.janela + 1)
                trecho = ("… " if lo > 0 else "") + " ".join(toks[lo:hi]) + (" …" if hi < len(toks) else "")
                wr.writerow([w, f"{ref[0]} {ref[1]}:{ref[2]}", trecho])
    resumo = {"versao_id": VERSION_ID, "versiculos": n_verses, "livros": len(book_info),
              "palavras": sum(occ.values()), "vocabulario": len(occ), "query": QUERY.strip()}
    (a.out / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in resumo.items() if k != "query"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
