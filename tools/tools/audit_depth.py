"""Independent, read-only whole-range source/published audit for Oklahoma q1511.

This does not call either existing statute parser or verifier. PDF text is read
directly, provision headings and printed legislative notes are inventoried, and
unchanged input text is checked against published Git blob hashes.
"""
from __future__ import annotations
import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata

HERE = Path(__file__).resolve().parents[1]
HEAD = re.compile(r'^\s*§\s*(\d+[A-Za-z]?)-(\S+?)\.\s+(.*)$')
RULE = re.compile(r'^\s*Rule\s+(\S+?)\.\s+(.*)$')
STUB = re.compile(r'^(Repealed|Renumbered|Superseded|Expired|Deleted|Omitted|Transferred|Reserved|Recodified|'
                  r'Executed|Annulled|Vacated|Unconstitutional|Blank|See the following versions|Amended by|Editorially)\b', re.I)
NOTE = re.compile(r'^(Added by|Amended by|Renumbered|Repealed by|R\.\s?L\.|Laws \d|L\.\s?\d|St\.\s?Supp|NOTE:|Note:|'
                  r'Historical Data|Source:|Derived from|Formerly|Comp\.\s?St|C\.\s?O\.\s?S|S\.\s?L\.|'
                  r'Initiative|State Question|Editorially|Recodified|Supersed|Promulgated by|Adopted by)')
EFF = re.compile(r'eff\.\s+([A-Z][a-z]+)\.?\s+(\d{1,2}),\s+(\d{4})')
MONTHS = dict(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], range(1,13)))
MONTHS.update({'June':6, 'July':7, 'Sept':9, 'March':3, 'April':4})

def letters(text):
    return re.sub('[^A-Za-z0-9]', '', unicodedata.normalize('NFKD', text))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--job', type=Path, required=True)
    args = ap.parse_args()
    job = args.job.resolve()
    evidence = job / 'evidence'
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    def pidlog(pid, desc):
        with (job / 'pids.txt').open('a', encoding='utf-8') as f:
            f.write(f'{pid} {desc}\n')
    pidlog(os.getpid(), 'python audit-depth')
    original_popen = subprocess.Popen
    class RecordedPopen(original_popen):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            pidlog(self.pid, 'audit child git')
    subprocess.Popen = RecordedPopen
    import pymupdf
    published = job / 'published'
    def git(*a):
        return subprocess.check_output(['git', '-C', str(published), *a], timeout=120)
    head = git('rev-parse', 'HEAD').decode().strip()
    tree = git('ls-tree', '-r', 'HEAD').decode('utf-8')
    (evidence/'published-tree.txt').write_text(tree,encoding='utf-8')
    blobs = {line.partition('\t')[2]: line.partition('\t')[0].split()[-1] for line in tree.splitlines()}
    versions = json.loads((evidence / 'published-data-versions.json').read_text('utf-8'))
    published_acts = {a['slug']: a for a in versions['acts']}
    report_path = evidence / 'depth-audit.json'
    report = json.loads(report_path.read_text('utf-8')) if report_path.exists() else {
        'published_head': head, 'titles': {}, 'constitution': {}, 'checks': []}
    note_path = evidence / 'source-history.tsv'
    if not note_path.exists():
        note_path.write_text('act\tsection\tpage\teffective_dates\tprinted_note\tsource_url\n', encoding='utf-8')
    for part in sorted((HERE / 'corpus.d').glob('title-*.json')):
        act = json.loads(part.read_text('utf-8'))['acts'][0]
        slug = act['slug']
        if slug in report['titles']:
            continue
        filename = act['url'].rsplit('/', 1)[-1]
        raw_path = evidence / filename
        if not raw_path.exists():
            continue  # collector still running; next invocation resumes these titles
        raw = raw_path.read_bytes()
        source_sha = hashlib.sha256(raw).hexdigest()
        doc = pymupdf.open(stream=raw, filetype='pdf')
        rows = []
        for pno, page in enumerate(doc):
            for line in page.get_text(sort=True).splitlines():
                if re.match(r'^\s*(Oklahoma Statutes(?: - Title .*|\s+Page \d+)?|Page \d+)\s*$', line):
                    continue
                rows.append((pno+1, line.strip()))
        doc.close()
        appendix = slug == 'title-74-appendix-1'
        tnum = act['short'].rsplit(' ',1)[-1]
        hre = RULE if appendix else re.compile(r'^\s*§\s*(' + re.escape(tnum) + r')-(\S+?)\.\s+(.*)$', re.I)
        headings = [(i, hre.match(line)) for i, (_,line) in enumerate(rows) if hre.match(line)]
        # Detect TOC by leader dots and the repeated first provision heading.
        start = 0
        if headings:
            first = headings[0][1].group(1 if appendix else 2)
            occurrences = [i for i,m in headings if m.group(1 if appendix else 2) == first]
            if len(occurrences) > 1:
                start = occurrences[1]
        sections = {}
        cur = None
        for page, line in rows[start:]:
            m = hre.match(line)
            if m:
                num = m.group(1 if appendix else 2)
                cur = {'number': num, 'page': page, 'heading': m.group(2 if appendix else 3), 'lines': []}
                sections.setdefault(num, []).append(cur)
            elif cur is not None:
                cur['lines'].append(line)
        units = act['versions'][-1]['units']
        published_blob_errors = []
        source_mismatches = []
        notes = []
        effective_dates = []
        for key, unit in units.items():
            data = unit['text'].encode('utf-8')
            oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if blobs.get(f'{slug}/{key}.md') != oid:
                published_blob_errors.append(key)
            num = unit['label'].rsplit('Rule ' if appendix else '§ ', 1)[-1]
            candidates = sections.get(num, [])
            expected = letters(unit['text'].split('\n',1)[0].split('. ',1)[-1] + ' ' + unit['text'].split('\n',1)[-1])
            found = False
            for sec in candidates:
                body = [sec['heading']]
                note = []
                in_note = False
                for ln in sec['lines']:
                    if NOTE.match(ln):
                        in_note = True
                    (note if in_note else body).append(ln)
                official = letters(' '.join(body))
                if official == expected:
                    found = True
                if note:
                    exact_note = ' '.join(note).strip()
                    dates = []
                    for mon, day, year in EFF.findall(exact_note):
                        try:
                            dates.append(dt.date(int(year), MONTHS[mon], int(day)).isoformat())
                        except (KeyError, ValueError):
                            pass
                    notes.append({'section':num, 'page':sec['page'], 'dates':dates, 'quote':exact_note})
                    effective_dates.extend(dates)
            if not found:
                source_mismatches.append({'key':key, 'number':num,
                                          'reason':'direct independent PDF reading-order/body boundary comparison differs'})
        raw_numbers = set(sections)
        retained_numbers = {u['label'].rsplit('Rule ' if appendix else '§ ',1)[-1] for u in units.values()}
        missing = []
        stubs = []
        for number in sorted(raw_numbers-retained_numbers):
            if all(STUB.match(s['heading']) or STUB.match(next((ln for ln in s['lines'] if ln.strip()), '')) for s in sections[number]):
                stubs.append(number)
            else:
                missing.append({'number':number, 'heading':sections[number][0]['heading'], 'page':sections[number][0]['page']})
        published_day = published_acts[slug]['versions'][-1]['from']
        latest_date = max(effective_dates) if effective_dates else None
        report['titles'][slug] = {
            'url':act['url'], 'source_sha256':source_sha,
            'matches_published_source_sha': source_sha == published_acts[slug]['versions'][-1]['sha256'],
            'units':len(units), 'published_blob_errors':published_blob_errors,
            'source_text_matches':len(units)-len(source_mismatches),
            'source_text_differences':source_mismatches,
            'missing_nonstub_candidates':missing, 'excluded_stub_count':len(stubs),
            'history_notes':len(notes), 'published_date':published_day,
            'latest_printed_effective_date':latest_date,
            'date_differs_from_latest_printed_effective':latest_date != published_day,
            'effective_dates_after_published_date':sorted(set(d for d in effective_dates if d>published_day)),
            'notes_are_published':False}
        with note_path.open('a',encoding='utf-8') as f:
            for n in notes:
                f.write('\t'.join([slug,n['section'],str(n['page']),','.join(n['dates']),n['quote'].replace('\t',' '),act['url']])+'\n')
        report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(f'{slug}: {len(units)} published units; {len(published_blob_errors)} blob differences; '
              f'{len(source_mismatches)} source-reading differences; {len(missing)} missing candidates; latest note {latest_date}',flush=True)
    cp = evidence / 'AllOKConstitutionArticles.pdf'
    if cp.exists() and not report['constitution']:
        doc = pymupdf.open(cp)
        text = '\n'.join(p.get_text(sort=True) for p in doc)
        (evidence/'constitution-source.txt').write_text(text,encoding='utf-8')
        amendment_dates = re.findall(r'(?:adopted at election held|adopted at election|adopted|approved)[^\n]{0,160}',text,re.I)
        report['constitution'] = {'source_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
                                 'published_source_sha256':published_acts['constitution']['versions'][-1]['sha256'],
                                 'pages':len(doc),'amendment_date_quotes':amendment_dates,
                                 'base_correction_supported':False}
        doc.close()
    report['checks'] = [
        'Published blob hashes compared with unchanged corpus unit bytes, across all available titles.',
        'Official PDF SHA256 compared with unchanged published data/versions.json source SHA256.',
        'Direct official PDF reading-order section bodies compared with unchanged corpus text, letters/digits only; differences held, not corrected.',
        'Official body heading identifiers compared with published unit identifiers; non-stub gaps remain candidates until reviewed.',
        'Printed legislative-history effective dates compared with published baseline dates; no file timestamp used as legal evidence.']
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Completed {len(report["titles"])} title audits',flush=True)

if __name__ == '__main__':
    main()
