"""Oklahoma: write repo/README.md, LICENSE, jurisdiction.json from corpus.json and corpus.d/."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'world-law'))
import us_state_lib as L

c = json.loads((HERE / 'corpus.json').read_text('utf-8'))
n_const = len(c['acts'][0]['versions'][0]['units'])
titles = []
for p in sorted((HERE / 'corpus.d').glob('title-*.json')):
    a = json.loads(p.read_text('utf-8'))['acts'][0]
    v = a['versions'][-1]
    titles.append((a['slug'], a['title'], len(v.get('units', {})), v['from']))
titles.sort(key=lambda t: t[0])
n_sec = sum(t[2] for t in titles)
days = sorted({t[3] for t in titles})
held = [t for t in titles if t[2] and 'appendix' not in t[0]]
app = [t for t in titles if 'appendix' in t[0]]
n_sec = sum(t[2] for t in held)
rep = json.loads((HERE / 'parse_statutes.report.json').read_text('utf-8'))
empty = sorted(k for k, v in rep.items() if not v['units'])


def fmt(d):
    import datetime as dt
    x = dt.date.fromisoformat(d)
    return f'{x.day} {x.strftime("%B")} {x.year}'


rows = '\n'.join(f'| `{s}/` | {t.replace("Oklahoma Statutes, ", "")} | {n:,} |' for s, t, n, _ in sorted(held + app))

README = f"""# Oklahoma: law history in git

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is the law of Oklahoma, United States, which global-law reads at `united-states/oklahoma/acts/`.

The Constitution of Oklahoma and the Oklahoma Statutes as a git repository: one file per section, one paragraph per line, so `git blame` works line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now**

- `constitution/`: the Constitution of the State of Oklahoma, {n_const} sections, one version (the Oklahoma State Senate's PDF of December 2019).
- `title-NN/`: the Oklahoma Statutes, one folder per title ({len(held)} titles, {n_sec:,} sections), and `title-74-appendix-1/`: Title 74's Appendix I, the Ethics Commission Rules ({app[0][2]} rules), one version each: the Legislature's edition of December 2025.

| Folder | Title | Sections |
| --- | --- | ---: |
{rows}

Titles whose every section has been repealed or renumbered ({', '.join(t.replace('title-', '').lstrip('0').upper() for t in empty)}) have no folder.

## Where the text comes from

- **Statutes:** the Oklahoma Legislature publishes each title of the Oklahoma Statutes as one PDF (with a text layer, made from Word) in the directory <https://www.oklegislature.gov/OK_Statutes/CompleteTitles/> (`os1.pdf` ... `os85A.pdf`). They were retrieved on 10 November 2026. The site states no reuse terms.
- **Constitution:** the Oklahoma State Senate publishes the whole Constitution as one PDF, <https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf> (made 21 December 2019, with a text layer).

## Dates

- The statute PDFs state no "current through" date. Each title is dated by its file's date on the Legislature's server ({' and '.join(fmt(d) for d in days)}; the PDFs' own creation dates agree): the edition carries the acts of the 2025 regular session. Some sections print text of 2025 acts that took effect later, on 1 January 2026 or 1 July 2026; each title's version note says how many. Acts of the 2026 session are not in this edition.
- The Constitution is dated **22 December 2019**, the date the Senate's server gives for its PDF.
- Every first version is credited to the publisher as "oldest version available": the PDFs give the current text only.

## What it does not show

- Earlier text of any section: the Legislature's site publishes only the current edition of each title, so there is no history before December 2025 here. Constitutional amendments adopted after December 2019 are not in the Constitution's text.
- Each section's history note ("Added by Laws ...", "Amended by Laws ...", "R.L. 1910, ...", "NOTE: ...") is left out, as are the tables of contents, page headers and footers, and the one-line stubs the edition keeps for repealed, renumbered, superseded or annulled sections.
- Where the edition prints two or more versions of a section (`§ ...v1`, `§ ...v2`: amendments by different acts that the Legislature has not reconciled), each is kept as its own file (`sec-...v1.md`, `sec-...v2.md`).
- Paragraph breaks are rebuilt from each PDF's indentation, so a break can be missing or extra, for example inside a table.
- Nothing here is an official publication or legal advice.

## How it is checked

- Every section's letters and digits were compared with a second, independent read of the same PDF.
- Every unit is read back from git on its day and compared with the corpus (`tools/check_repo.py`; results in `REPRODUCE.md`).
- The source of each version is identified by its sha256, in `data/versions.json`.
"""

LICENSE = """The legal text is the Constitution of the State of Oklahoma as published by the Oklahoma State Senate (Legislative Service Bureau)
at https://oksenate.gov/sites/default/files/2019-12/AllOKConstitutionArticles.pdf, and the Oklahoma Statutes as published by the
Oklahoma Legislature at https://www.oklegislature.gov/OK_Statutes/CompleteTitles/.

Neither site states reuse terms, and the PDFs carry no notice. The Constitution and statutes of a state are official legal texts
and edicts of government that copyright does not protect (Georgia v. Public.Resource.Org, Inc., 590 U.S. 255 (2020)). They are
republished here, unaltered except for the changes below, with credit to the Oklahoma Legislature as their publisher.

Changes made by Lexifina: one Markdown file per section, one paragraph per line, normalised spaces, quotation marks and hyphens;
repealed sections, the editorial history notes, tables of contents and page headers and footers left out. The wording of the law was
not changed. The Oklahoma Legislature does not endorse this repository.

Lexifina's own contributions (the arrangement of the history, the commit messages, the tables and the tools) are dedicated to the
public domain under CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""

L.write_repo(HERE, README, LICENSE, {
    'path': 'us-ok', 'code': 'OK', 'name': 'Oklahoma', 'level': 'state',
    'repo': 'https://github.com/lexifina/united-states-oklahoma-law',
    'build': f'built: Constitution (Oklahoma State Senate PDF of December 2019) and the Oklahoma Statutes ({len(held)} titles, '
             f'{n_sec} sections, Legislature PDFs of December 2025), one version each',
    'register_date': '2026-10-30'})
