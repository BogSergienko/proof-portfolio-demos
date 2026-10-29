#!/usr/bin/env python3
"""KAI Proof / synthetic agent-event audit (stdlib only).

Demonstrates evidence checking and STOP; not a test of any LLM model.
Run: python proof_check.py
"""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parent

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sha256(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def audit(doc):
    evidence = doc['evidence']
    stopped = set(doc['stopped_tasks'])
    findings = []
    for action in doc['agent_actions']:
        ref = action['evidence_id']
        status = None
        reason = None
        if action['task_id'] in stopped and action['effect'] != 'read_only':
            status, reason = 'BLOCKED_STOP', 'A write/action was attempted after task STOP.'
        elif ref not in evidence:
            status, reason = 'UNVERIFIED', 'Referenced evidence does not exist.'
        else:
            item = evidence[ref]
            if item['checksum'] != sha256(item['data']):
                status, reason = 'INTEGRITY_FAIL', 'Evidence content checksum is invalid.'
            elif action['evidence_version'] != item['version']:
                status, reason = 'STALE_VERSION', 'Claim cites a non-current source version.'
            elif action['field'] not in item['data']:
                status, reason = 'UNVERIFIED', 'Claimed field is absent from source.'
            elif action['claimed_value'] != item['data'][action['field']]:
                status, reason = 'VALUE_MISMATCH', 'Claim does not equal source field value.'
            else:
                status, reason = 'VERIFIED', 'Current source and claim match; no STOP violation.'
        findings.append({'id': action['id'], 'status':status, 'reason':reason,
                         'task_id':action['task_id'], 'claim':action['claim'],
                         'source':ref, 'effect': action['effect']})
    return findings

def main():
    source = json.loads((ROOT / 'synthetic_case.json').read_text(encoding='utf-8',newline='\n'))
    findings = audit(source)
    actual = {item['id']: item['status'] for item in findings}
    expected = source['expected_statuses']
    if actual != expected:
        print('FAIL expected', expected, '\nactual', actual)
        return 1
    verified = sum(x['status']=='VERIFIED' for x in findings)
    summary = {
        'title':'KAI Proof / bounded synthetic audit',
        'tests_passed':len(findings),
        'verified_claims':verified,
        'flagged_or_blocked':len(findings)-verified,
        'statuses':actual,
        'limitations':'Synthetic logs only; not an LLM evaluation, not secure access enforcement, not evidence authenticity proof.'
    }
    (ROOT/'RESULT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    md = ['# KAI Proof — демонстрационный аудит', '',
          'Данные вымышленные. Пример не оценивает реальную модель ИИ и не доказывает безопасность системы.', '',
          '| Событие | Решение | Почему |', '|---|---|---|']
    md += [f"| {x['id']} | {x['status']} | {x['reason']} |" for x in findings]
    md += ['', f"Подтверждено: {verified}; выявлено/заблокировано: {len(findings)-verified}.",
           'PASS означает совпадение с заранее заданным тестовым эталоном, а не доказанное снижение ошибок реального ИИ.']
    (ROOT/'REPORT.md').write_text('\n'.join(md)+'\n',encoding='utf-8',newline='\n')
    for x in findings: print(f"{x['id']}: {x['status']}")
    print(f'PASS: {len(findings)}/{len(findings)} synthetic checks. REPORT.md and RESULT.json created.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
