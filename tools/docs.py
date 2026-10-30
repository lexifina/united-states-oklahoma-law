"""Oklahoma: write repo/README.md, LICENSE, jurisdiction.json."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'world-law'))
import us_state_lib as L

c = json.loads((HERE / 'corpus.json').read_text('utf-8'))
n = len(c['acts'][0]['versions'][0]['units'])

README = f"""# Oklahoma: law history in git

The Constitution of Oklahoma as a git repository: one file per section ({n} provisions), one paragraph per line, so `git blame` works line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the State of Oklahoma | 1 | Oldest version available: the Oklahoma State Senate's PDF of December 2019 |

That is all the law this repository holds today. **The Oklahoma Statutes are not in it**: the Legislature's site (oklegislature.gov) forbids every crawler in its robots.txt, and the Supreme Court Network's statute site (oscn.net) could not be reached, so no statute was taken.

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
"""

LICENSE = """The legal text is the Constitution of the State of Oklahoma as published by the Oklahoma State Senate (Legislative Service Bureau)
at https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf.

The page and the file state no reuse terms that could be read: the site's HTML pages gave no content to an automated client, and the
PDF carries no notice. A state constitution is an official legal text and an edict of government that copyright does not protect
(Georgia v. Public.Resource.Org, Inc., 590 U.S. 255 (2020)). It is republished here, unaltered except for the changes below, with credit to
the Oklahoma State Senate as its publisher.

Changes made by Lexifina: one Markdown file per section, one paragraph per line, normalised spaces, quotation marks and hyphens;
repealed sections, the editorial amendment notes and page footers left out. The wording of the law was not changed. The Oklahoma State
Senate does not endorse this repository.

Lexifina's own contributions (the arrangement of the history, the commit messages, the tables and the tools) are dedicated to the
public domain under CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""

L.write_repo(HERE, README, LICENSE, {
    'path': 'us-ok', 'code': 'OK', 'name': 'Oklahoma', 'level': 'state',
    'repo': 'https://github.com/lexifina/united-states-oklahoma-law',
    'build': 'built: Constitution only, one version (Oklahoma State Senate PDF of December 2019, dated 2019-12-22); statutes not taken (robots.txt)',
    'register_date': '2026-10-30'})
