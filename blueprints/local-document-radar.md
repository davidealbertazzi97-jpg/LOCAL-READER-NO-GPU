# Local Document Radar

## One-sentence product

Private semantic search and change detection across folders chosen by the user,
with every result linked to the exact file, page, and passage that supports it.

## What it actually does

The user selects one or more folders. The application reads supported files,
extracts their text locally, divides it into short passages, and creates a local
search index. A question such as “where did we define the cancellation period?”
can then find passages containing “notice of withdrawal” even when the exact
words differ.

This is a **radar**, not an automatic chatbot. Its first screen should show
evidence:

- matching passage and highlighted terms;
- file name, folder, page or section, modification date;
- why it matched and a transparent relevance score;
- duplicate, near-duplicate, and newer-version indicators.

The app never moves, renames, edits, or deletes source documents. Removing a
folder from the radar removes only its local index.

## First useful release

1. Explicit folder allow-list; no whole-disk scan.
2. PDF, DOCX, TXT, Markdown, and ODT text extraction.
3. Exact search plus multilingual semantic search in Italian and English.
4. Filters by folder, type, date, and modified-since-last-scan.
5. Duplicate and probable-new-version groups.
6. “Open source file” and “copy citation” actions.
7. Index pause, rebuild, export diagnostics, and complete local deletion.

OCR for image-only PDFs should be an optional adapter shared with the
accessibility project, not a hidden mandatory dependency.

## Architecture and safeguards

- SQLite FTS for exact search.
- A small multilingual embedding model, chosen only after CPU/RAM and licence
  tests, for semantic search.
- Content hashes prevent unnecessary re-indexing.
- The index stores passages, so it is confidential data: private permissions,
  clear delete controls, and no sensitive snippets in logs.
- Retrieval answers, if added later, must cite indexed passages and distinguish
  quotes from generated summaries.

## Acceptance test

On a folder of 1,000 mixed office documents on an ordinary four-core CPU, a
second scan must skip unchanged files; a query must return useful cited
passages without any external network connection or source-file mutation.
