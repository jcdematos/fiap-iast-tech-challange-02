"""
Reads the per-column profiles produced by censo_escolar_profile.py for 2023
and 2024 and prints the null% distribution, the fully-null/constant columns,
a breakdown of the sparse (>25% null) columns, and a check on a few columns
the project's join/streaming design depends on. This is what
censo_escolar_findings.md is a write-up of.

Usage:
    python censo_escolar_analyze.py [2023_json] [2024_json]

Defaults to censo_escolar_2023.json / censo_escolar_2024.json next to this
script.
"""
import json
import os
import sys

KEY_COLUMNS = [
    'CO_MUNICIPIO', 'TP_DEPENDENCIA', 'TP_LOCALIZACAO',
    'QT_MAT_FUND_AI_2', 'QT_MAT_FUND_AI_1',
    'IN_BIBLIOTECA', 'IN_ACESSO_INTERNET_COMPUTADOR', 'IN_INTERNET',
    'NU_ANO_CENSO', 'CO_ENTIDADE',
]


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def null_pct_bucket(pct):
    if pct == 0:
        return '0%'
    if pct == 100:
        return '100%'
    if pct < 25:
        return '0-25%'
    if pct < 50:
        return '25-50%'
    if pct < 75:
        return '50-75%'
    return '75-99%'


def summarize(profile, label):
    rc = profile['row_count']
    results = profile['results']

    all_null = [r for r in results if r['nulls'] == rc]
    constant = [r for r in results if r['nulls'] < rc and not r['capped'] and r['distinct_sample_count'] == 1]

    buckets = {'0%': 0, '0-25%': 0, '25-50%': 0, '50-75%': 0, '75-99%': 0, '100%': 0}
    for r in results:
        buckets[null_pct_bucket(r['pct_null'])] += 1

    print(f'--- {label}: rows={rc} cols={profile["columns"]} ---')
    print('null% distribution:', buckets)
    print(f'FULLY NULL columns ({len(all_null)}):', [r['col'] for r in all_null])
    print(f'CONSTANT (single value) columns ({len(constant)}):')
    for r in constant:
        print('   ', r['col'], '-> value:', r['sample'], f"(null={r['pct_null']}%)")
    print()

    return {r['col']: r for r in results}


def bucket_list(profile, lo, hi, label):
    cols = [(r['col'], r['pct_null']) for r in profile['results'] if lo <= r['pct_null'] < hi]
    cols.sort(key=lambda x: -x[1])
    print(f'{label} ({len(cols)}):')
    for c, p in cols:
        print(f'   {c}: {p}%')
    print()


def key_column_check(m23, m24):
    print('--- Key columns check ---')
    for c in KEY_COLUMNS:
        r23 = m23.get(c)
        r24 = m24.get(c)
        print(c, '| 2023 null%:', r23['pct_null'] if r23 else 'MISSING', 'sample:', r23['sample'][:5] if r23 else None)
        print(' ' * len(c), '| 2024 null%:', r24['pct_null'] if r24 else 'MISSING', 'sample:', r24['sample'][:5] if r24 else None)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    path_2023 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'censo_escolar_2023.json')
    path_2024 = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'censo_escolar_2024.json')

    profile_2023 = load(path_2023)
    profile_2024 = load(path_2024)

    m23 = summarize(profile_2023, '2023')
    m24 = summarize(profile_2024, '2024')

    print('=== 2023 sparse columns ===')
    bucket_list(profile_2023, 75, 100, '75-99% null')
    bucket_list(profile_2023, 50, 75, '50-75% null')
    bucket_list(profile_2023, 25, 50, '25-50% null')

    print('=== 2024 sparse columns ===')
    bucket_list(profile_2024, 75, 100, '75-99% null')
    bucket_list(profile_2024, 50, 75, '50-75% null')
    bucket_list(profile_2024, 25, 50, '25-50% null')

    key_column_check(m23, m24)
