"""Independent fixture checks, no external packages, no network calls."""
import copy
import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'cases/orders'
A=ROOT/'cases/evidence-audit'


def load_auditor():
    spec=importlib.util.spec_from_file_location('public_audit_demo',A/'proof_check.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class OrdersTests(unittest.TestCase):
    def run_orders(self, customize=None):
        tmp=tempfile.TemporaryDirectory()
        p=Path(tmp.name)
        for name in ['process_orders.py','Выгрузка_магазин.csv','Выгрузка_касса.csv']:
            shutil.copy2(O/name,p/name)
        if customize:
            customize(p)
        proc=subprocess.run([sys.executable,str(p/'process_orders.py')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(0,proc.returncode,proc.stderr)
        return tmp,p

    def test_bundled_outputs_exact_bytes(self):
        temp,p=self.run_orders()
        try:
            for name in ['01_Проверенные_заказы.csv','02_Проблемные_строки.csv','03_Сводка.csv','04_Показатели.json']:
                self.assertEqual((O/name).read_bytes(),(p/name).read_bytes(),name)
        finally:temp.cleanup()

    def test_counts_conserve_rows(self):
        v=json.loads((O/'04_Показатели.json').read_text(encoding='utf-8'))
        self.assertEqual((v['входных_строк'],v['проверенных_строк'],v['проблемных_строк']),(138,111,27))
        self.assertEqual(v['дубликатов'],14)
        self.assertEqual(v['несовпадений_сумм'],9)
        self.assertEqual(v['ошибок_формата'],4)
        self.assertEqual(v['выручка_после_возвратов_руб'],169620)
        self.assertEqual(v['входных_строк'],v['проверенных_строк']+v['проблемных_строк'])

    def test_input_generator_reproduces_originals(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            shutil.copy2(O/'generate_example.py',p/'generate_example.py')
            proc=subprocess.run([sys.executable,str(p/'generate_example.py')],capture_output=True,timeout=20)
            self.assertEqual(0,proc.returncode,proc.stderr.decode(errors='replace'))
            for name in ['Выгрузка_магазин.csv','Выгрузка_касса.csv']:
                self.assertEqual((O/name).read_bytes(),(p/name).read_bytes(),name)

    def test_introduced_wrong_amount_is_flagged(self):
        def tamper(p):
            csvpath=p/'Выгрузка_магазин.csv'
            with csvpath.open('r',encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f,delimiter=';')
                fields=reader.fieldnames
                rows=list(reader)
            rows[0]['сумма']=str(int(rows[0]['сумма'])+1)
            with csvpath.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields,delimiter=';');writer.writeheader();writer.writerows(rows)
        temp,p=self.run_orders(tamper)
        try:
            v=json.loads((p/'04_Показатели.json').read_text('utf-8'))
            self.assertEqual(v['проверенных_строк'],110)
            self.assertEqual(v['проблемных_строк'],28)
            with (p/'02_Проблемные_строки.csv').open(encoding='utf-8-sig',newline='') as f:
                rows=list(csv.DictReader(f,delimiter=';'))
            self.assertTrue(any(x['причина']=='Сумма не совпадает с количеством × ценой' for x in rows))
        finally:temp.cleanup()

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod=load_auditor()
        cls.doc=json.loads((A/'synthetic_case.json').read_text(encoding='utf-8'))

    def test_seven_fixture_classifications(self):
        found={x['id']:x['status'] for x in self.mod.audit(self.doc)}
        self.assertEqual(found,self.doc['expected_statuses'])
        self.assertEqual(len(found),7)
        self.assertEqual(sum(x=='VERIFIED' for x in found.values()),2)

    def test_wrong_value_detected(self):
        d=copy.deepcopy(self.doc)
        first=d['agent_actions'][0]
        first['claimed_value']='not the source value'
        self.assertEqual(self.mod.audit(d)[0]['status'],'VALUE_MISMATCH')

    def test_missing_source_detected(self):
        d=copy.deepcopy(self.doc);d['agent_actions'][0]['evidence_id']='MISSING-REFERENCE'
        self.assertEqual(self.mod.audit(d)[0]['status'],'UNVERIFIED')

    def test_inconsistent_source_integrity_detected(self):
        d=copy.deepcopy(self.doc)
        ref=d['agent_actions'][0]['evidence_id']
        d['evidence'][ref]['data']['tampered']='yes'
        self.assertEqual(self.mod.audit(d)[0]['status'],'INTEGRITY_FAIL')

    def test_stale_version_detected(self):
        d=copy.deepcopy(self.doc);d['agent_actions'][0]['evidence_version']=-900
        self.assertEqual(self.mod.audit(d)[0]['status'],'STALE_VERSION')

    def test_stop_blocks_logged_write(self):
        d=copy.deepcopy(self.doc)
        first=d['agent_actions'][0]
        d['stopped_tasks'].append(first['task_id'])
        first['effect']='write'
        self.assertEqual(self.mod.audit(d)[0]['status'],'BLOCKED_STOP')

    def test_reproduces_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for name in ['proof_check.py','synthetic_case.json']:
                shutil.copy2(A/name,p/name)
            r=subprocess.run([sys.executable,str(p/'proof_check.py')],capture_output=True,text=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn('PASS: 7/7 synthetic checks',r.stdout)
            for name in ['RESULT.json','REPORT.md']:
                self.assertEqual((A/name).read_bytes(),(p/name).read_bytes(),name)

class PackagingTests(unittest.TestCase):
    def test_index_and_case_pages_exist(self):
        page=(ROOT/'docs/index.html').read_text(encoding='utf-8')
        for path in ('orders.html','evidence.html','assets/orders_before_after.png'):
            self.assertIn(path,page)
            self.assertTrue((ROOT/'docs'/path).is_file())

    def test_release_hashes(self):
        for row in (ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
            if not row.strip(): continue
            sha,rel=row.split('  ',1)
            self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),sha,rel)

if __name__=='__main__':unittest.main()
