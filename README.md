# Oklahoma: law history in git

The Constitution of Oklahoma as a git repository: one file per section (404 provisions), one paragraph per line, so `git blame` works line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the State of Oklahoma | 1 | Oldest version available: the Oklahoma State Senate's PDF of December 2019 |

That is all the law this repository holds today.

## Where the text comes from

The Oklahoma State Senate publishes the whole Constitution as one PDF, <https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf> (made 21 December 2019, with a text layer). The site states no reuse terms that could be read.

## Dates

- The single version is dated **22 December 2019**, the date the Senate's server gives for the PDF. It is the oldest version available; the PDF carries no in-force date, and the PDF's own notes name only the State Question behind each amendment.
- The first commit is credited to the publisher as "oldest version available".

## What it does not show

- Any amendment adopted after the December 2019 PDF, and any history before it.
- Repealed sections, and the editorial notes under each section ("Amended by State Question No. ..."), are left out. Where a section has a version "effective until Oct. 1, 2018" and a later text, the later text is used.
- Paragraph breaks are rebuilt from the PDF's line layout, so a break can be missing or extra in a long section.
- Nothing here is an official publication or legal advice.

## How it is checked

- Every unit is read back from git on its day and compared with the corpus (`tools/check_repo.py`; results in `REPRODUCE.md`).
- The source is identified by its sha256, in `data/versions.json`.
