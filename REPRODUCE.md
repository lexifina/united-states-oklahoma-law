# How this repository was made (Oklahoma)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Oklahoma Constitution (Oklahoma State Senate, PDF) | <https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf> | 2026-10-30 | no reuse terms found; official text of a state constitution |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of the State of Oklahoma | 1 | 2019-12-22 to 2019-12-22 |

The build made 1 commits:

| Commits | Kind |
| ---: | --- |
| 1 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 0 laws in the record.
- 1 tags.

## Dates

Each commit is dated at noon (America/Chicago) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Oklahoma Constitution Art. 5, sec. 58: an act takes effect 90 days after the Legislature adjourns, unless passed as an emergency measure. https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `efb7bb0a891b0d9e0cc91ff6b3ad301f7826ed8fb71072c0b5672025af93ce37` (551616 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- The Oklahoma Statutes could not be taken. No page was fetched from either. This build holds the Constitution only.
- The Constitution is the Oklahoma State Senate's PDF of the whole Constitution (made 21 December 2019). It has no in-force date, so the version is dated 2019-12-22, the PDF's Last-Modified date on the Senate server. Amendments adopted after that PDF are not in it.
- Repealed sections (those whose heading says "Repealed by State Question ...") and the editorial notes under each section ("Amended by State Question No. ... adopted at election ...") are left out; page footers are dropped. Paragraph breaks are rebuilt from the PDF's line layout: a break before an (a)-style marker and after a short line ending in a full stop.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code wrote the parse script; it wrote or changed no legal text. The script is deterministic and runs no model.
