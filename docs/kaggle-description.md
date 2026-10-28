**Palavras da Bíblia**: every word of the Portuguese Bible in the *Almeida Revista e Atualizada* (1993), counted. **592,643 words, 30,127 distinct**, 66 books, 1,189 chapters, 31,104 verses. For each word: occurrences, verses, chapters, books, and occurrences in the Old and New Testament; the count of every word in every book; the characteristic words of each book; and 114 short quoted excerpts.

The translation is protected by copyright, so the text itself is not here: only counts, and excerpts of a few words each, with their reference.

![The 25 most frequent words](https://raw.githubusercontent.com/CaiqueDourado/palavras-da-biblia/main/docs/img/top-words.png)

## What the counts show

- **Senhor** (Lord) leads with 8,046 occurrences, 7,327 of them in the Old Testament; **Deus** has 4,438; **Jesus** (1,180) appears only in the New Testament.
- **309 function words** (de, que, os, do, para…) are 48.9% of everything written; **13,268 words appear only once** (44% of the vocabulary).
- **fé** (faith) appears 248 times in the New Testament and **once** in the Old: "… justo viverá pela sua fé." (Habakkuk 2:4).
- One word per book: noemi in Ruth, preguiçoso (the sluggard) in Proverbs, gafanhoto (the locust) in Joel, saulo in Acts, besta (the beast) in Revelation.

![One word per book](https://raw.githubusercontent.com/CaiqueDourado/palavras-da-biblia/main/docs/img/one-word-per-book.png)

![Words of the Old and of the New Testament](https://raw.githubusercontent.com/CaiqueDourado/palavras-da-biblia/main/docs/img/at-vs-nt.png)

## Files

- `palavras.csv`: one row per word: occurrences, verses, chapters, books, Old and New Testament, first book, `funcional` (function word).
- `palavras_por_livro.csv`: occurrences of each word in each book.
- `livros.csv`: the 66 books with chapters, verses, words and vocabulary.
- `palavras_caracteristicas.csv`: up to 5 characteristic words per book, with the index.
- `contextos.csv`: up to 3 short excerpts for 38 words, at most 4 words on each side, with the reference.
- `stats.json`: totals.

Read the CSVs with `keep_default_na=False`: the word "nan" would otherwise become a missing value.

## How it was made

![Method](https://raw.githubusercontent.com/CaiqueDourado/palavras-da-biblia/main/docs/img/flow.png)

The author's site **versiculo-do-dia.com** (2022) had a page per book, chapter and verse and a page "Palavras que mais aparecem na Bíblia" (the words that appear most). This dataset is that word index, rebuilt from the same SQL Server database: a script on the author's machine reads the verses, splits them into words (lower case, accents kept, hyphenated forms as one word, 2+ letters) and writes only the counts and the excerpts. The verse text is never written.

![versiculo-do-dia.com](https://raw.githubusercontent.com/CaiqueDourado/CaiqueDourado/main/assets/versiculo-do-dia.com_screenshot.png)

![The words of the Bible](https://raw.githubusercontent.com/CaiqueDourado/palavras-da-biblia/main/docs/img/cover.png)

Scripts, method, limits and the study in Portuguese and English: **https://github.com/CaiqueDourado/palavras-da-biblia**

## License

Counts, flags and indexes: CC BY 4.0. The excerpts are short quotations of the *Almeida Revista e Atualizada*, 2nd edition, © 1993 Sociedade Bíblica do Brasil, used for study with their reference, and are not covered by the CC license. Version 1.0.0. Author: Caique Dourado.
