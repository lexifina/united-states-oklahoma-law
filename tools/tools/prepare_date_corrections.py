"""Prepare five source-dated metadata corrections from unchanged title parts.

This copies all law-text units verbatim from existing parts. It checks the
official PDF hash and effective-date quote before writing each new part.
No publication marker is created here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SELECTION = {
    'title-07': ('os7.pdf', '2019-11-01', 'Laws 2019, c. 51, § 1, eff. Nov. 1, 2019.', 3),
    'title-08': ('os8.pdf', '2021-11-01', 'Added by Laws 2021, c. 198, § 1, eff. Nov. 1, 2021.', 17),
    'title-27': ('os27.pdf', '2025-11-01', 'Laws 2025, c. 489, § 1, eff. Nov. 1, 2025.', 4),
    'title-31': ('os31.pdf', '2024-11-01', 'Laws 2024, c. 70, § 1, eff. Nov. 1, 2024.', 4),
    'title-85': ('os85.pdf', '2024-07-01', '§85-380. Renumbered as § 85.70 of Title 74 by Laws 2024, c. 256, § 3, eff. July 1, 2024.', 35),
}

def compact(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--check', action='store_true', help='compare a second parse byte for byte without writing parts')
    parser.add_argument('--only', choices=sorted(SELECTION))
    parser.add_argument('--refresh-pending', action='store_true', help='rewrite only an existing pending part and its marker')
    args = parser.parse_args()
    evidence = args.evidence
    rows = []
    selection = {args.only: SELECTION[args.only]} if args.only else SELECTION
    for slug, (filename, day, quote, page_number) in selection.items():
        part_name = f'{slug}.json'
        original = json.loads((ROOT / 'corpus.d' / part_name).read_text(encoding='utf8'))
        act = original['acts'][0]
        version = act['versions'][-1]
        raw = (evidence / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != version['sha256']:
            raise ValueError(f'{slug}: official PDF differs from published source hash')
        pdf = pymupdf.open(stream=raw, filetype='pdf')
        page = compact(pdf[page_number - 1].get_text())
        pdf.close()
        if compact(quote) not in page:
            raise ValueError(f'{slug}: effective-date quotation absent from official PDF page {page_number}')
        if version['from'] == day:
            raise ValueError(f'{slug}: correction already present in original part')
        corrected = copy.deepcopy(act)
        changed = corrected['versions'][-1]
        changed['from'] = day
        note_kind = 'latest printed section-transfer note' if slug == 'title-85' else 'latest printed effective-date note'
        changed['note'] = (
            f'{act["title"]}: this is the unchanged text of the Legislature PDF edition, '
            f'with title-level in-force day {day} from the {note_kind}. '
            'The earlier part used the PDF file date. Section history notes remain excluded.'
        )
        basis = f'Oklahoma Legislature, {filename} p. {page_number}: {quote}'
        changed['correction'] = {
            'metadata_only': True,
            'reason': 'Correct the title-level in-force day from the PDF file date to the latest explicit effective date printed in the official section history.',
            'in_force_basis': basis,
        }
        if changed['units'] != version['units']:
            raise AssertionError(f'{slug}: law text changed')
        output = {
            'corrects': part_name,
            'acts': [corrected],
            'decisions': [f'{slug}: published date {version["from"]}; source effective date {day}. {basis} Law text copied unchanged from {part_name}.'],
            'ai_use': ['Model selected official printed effective-date metadata; law text copied byte for byte from the earlier published part.'],
        }
        outpath = ROOT / 'corpus.d' / f'zz-date-{slug}.json'
        rendered = json.dumps(output, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            if outpath.read_text(encoding='utf8') != rendered:
                raise ValueError(f'{slug}: second parse differs')
        elif args.refresh_pending:
            marker = outpath.with_suffix('.PUBLISH.pending')
            if outpath.with_suffix('.PUBLISH').exists() or not outpath.exists() or not marker.exists():
                raise ValueError(f'{slug}: refresh requires an existing pending part and no PUBLISH marker')
            outpath.write_text(rendered, encoding='utf8')
            marker.write_text('sha256:' + hashlib.sha256(outpath.read_bytes()).hexdigest() + '\n'
                              'worker: q-1567; corrected after independent review\n', encoding='utf8')
        else:
            if outpath.exists() or outpath.with_suffix('.PUBLISH').exists():
                raise FileExistsError(outpath)
            outpath.write_text(rendered, encoding='utf8')
        rows.append({'slug': slug, 'part': outpath.name, 'source_sha256': digest,
                     'published_date': version['from'], 'source_date': day,
                     'source_quote': quote, 'source_page': page_number,
                     'units_unchanged': len(version['units'])})
    if not args.check:
        (evidence / 'date-corrections.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(rows, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
