"""Real HTTP, signals, model subprocess and SQLite, using only local fixtures."""
import concurrent.futures
import json
import os
from pathlib import Path
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch, Mock
from test_adapter import adapter
from test_invoice_metadata import metadata, TEXT

HERE=Path(__file__).resolve().parent

class LifecycleTests(unittest.TestCase):
    def test_metadata_readiness_and_draining_never_invoke_model(self):
        with tempfile.TemporaryDirectory() as d, patch.object(adapter,'HOME',Path(d)), patch.object(adapter,'WORK',Path(d)/'paperless'), patch.object(adapter.subprocess,'Popen') as model:
            home=Path(d); (home/'codex').mkdir(); (home/'paperless/work').mkdir(parents=True)
            adapter.initialize_ledger()
            auth=home/'codex/auth.json'; auth.touch(mode=0o600)
            self.assertFalse(adapter.readiness()['ready'])
            auth.write_text('{}'); auth.chmod(0o660)
            adapter.protect_auth_metadata()
            self.assertEqual(auth.stat().st_mode & 0o777,0o600)
            self.assertEqual(auth.read_text(),'{}')
            self.assertTrue(adapter.readiness()['ready'])
            auth.chmod(0o644); self.assertFalse(adapter.readiness()['ready']); auth.chmod(0o600)
            adapter.DRAINING.set()
            try:
                self.assertFalse(adapter.readiness()['ready'])
                with self.assertRaisesRegex(RuntimeError,'Draining'):adapter.infer('cached fixture',False)
            finally:adapter.DRAINING.clear()
            model.assert_not_called()

    def test_ledger_failure_does_not_cache_success_or_leak_capacity(self):
        model=Mock(returncode=0)
        model.communicate.return_value=(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'{"text":"fixture"}'}}).encode(),None)
        with tempfile.TemporaryDirectory() as d, patch.object(adapter,'WORK',Path(d)), patch.object(adapter,'record',side_effect=RuntimeError('ledger failed')) as ledger, patch.object(adapter.subprocess,'Popen',return_value=model):
            (Path(d)/'work').mkdir()
            key=adapter.hashlib.sha256(b'Falseledger failure fixture').hexdigest()
            with self.assertRaisesRegex(RuntimeError,'ledger failed'):adapter.infer('ledger failure fixture',False)
            self.assertNotIn(key,adapter.CACHE)
            ledger.assert_called_once()
            self.assertTrue(adapter.WORKER.acquire(False));adapter.WORKER.release()
            self.assertTrue(adapter.ADMISSION.acquire(False));adapter.ADMISSION.release()

    def test_absolute_connection_deadline_bounds_slow_client(self):
        with patch.object(adapter,'CONNECTION_DEADLINE',.1):
            server=adapter.Server(('127.0.0.1',0),adapter.Handler)
            thread=adapter.threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                with socket.create_connection(server.server_address) as client:
                    client.sendall(b'GET /live HTTP/1.1\r\nX-Slow: ')
                    client.settimeout(1)
                    self.assertEqual(client.recv(1),b'')
            finally:
                server.shutdown();server.server_close();thread.join(timeout=1)
            self.assertFalse(thread.is_alive())

    def test_sigterm_joins_active_cancels_queued_and_retry_conserves_ledger(self):
        self.exercise(False)

    def test_timeout_kills_real_model_process_and_retry_conserves_ledger(self):
        self.exercise(True)

    def exercise(self, timeout):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d); (home/'codex').mkdir(); auth=home/'codex/auth.json'; auth.touch(mode=0o600)
            # Empty auth deliberately bypasses only the metadata gate in this fixture.
            # No Codex executable, network integration or live volume is available.
            model=home/'model.py'
            model.write_text('import json,pathlib,sys,time\np=pathlib.Path(sys.argv[1]);p.write_text(str(__import__("os").getpid()))\nsys.stdin.read()\ntime.sleep(float(sys.argv[2]))\nprint(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":sys.argv[3]}}))\nprint(json.dumps({"type":"turn.completed","usage":{"input_tokens":2,"output_tokens":1,"cached_input_tokens":0}}))\n')
            runner=home/'runner.py'
            runner.write_text('''import pathlib,sys
sys.path.insert(0,sys.argv[1])
import adapter as a
a.HOME=pathlib.Path(sys.argv[2]);a.WORK=a.HOME/'paperless'
a.TIMEOUT=float(sys.argv[4])
a.command=lambda path:[sys.executable,str(a.HOME/'model.py'),str(a.HOME/'started'),sys.argv[5],sys.argv[6]]
a.readiness=lambda:{'ready':not a.DRAINING.is_set(),'draining':a.DRAINING.is_set()}
a.serve(('127.0.0.1',int(sys.argv[3])))
''')
            with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            url=f'http://127.0.0.1:{port}'
            payload=json.dumps({'model':adapter.MODEL,'content':TEXT}).encode()
            def launch(limit, delay):
                p=subprocess.Popen([sys.executable,str(runner),str(HERE),d,str(port),str(limit),str(delay),json.dumps(metadata())],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                for _ in range(200):
                    try:
                        urllib.request.urlopen(url+'/live',timeout=.2).close();return p
                    except OSError:time.sleep(.01)
                p.kill();self.fail('fixture startup failed')
            def request(body=payload):
                try:
                    with urllib.request.urlopen(urllib.request.Request(url+'/v1/invoice-metadata',body),timeout=8) as r:return r.status,json.load(r)
                except urllib.error.HTTPError as e:return e.code,None
            p=launch(.3 if timeout else 3,2 if timeout else 1)
            try:
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    first=pool.submit(request)
                    for _ in range(200):
                        if (home/'started').exists():break
                        time.sleep(.01)
                    self.assertTrue((home/'started').exists())
                    pid=int((home/'started').read_text())
                    if timeout:
                        self.assertEqual(first.result()[0],503)
                    else:
                        queued=pool.submit(request,json.dumps({'model':adapter.MODEL,'content':TEXT+'\nqueued'}).encode())
                        time.sleep(.15)
                        began=time.monotonic();p.send_signal(signal.SIGTERM)
                        self.assertEqual(first.result()[0],200)
                        self.assertEqual(queued.result()[0],503)
                        out,err=p.communicate(timeout=5)
                        self.assertLess(time.monotonic()-began,3)
                        self.assertEqual((p.returncode,out,err),(0,b'',b''))
                    with self.assertRaises(ProcessLookupError):os.kill(pid,0)
                if p.poll() is None:p.send_signal(signal.SIGTERM);p.communicate(timeout=5)
                p=launch(3,.01)
                self.assertEqual(request()[0],200)
                p.send_signal(signal.SIGTERM);out,err=p.communicate(timeout=5)
                self.assertEqual((p.returncode,out,err),(0,b'',b''))
                with sqlite3.connect(home/'paperless/usage.sqlite') as db:
                    self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
                    rows=db.execute('SELECT outcome,input_tokens,output_tokens FROM requests ORDER BY rowid').fetchall()
                expected=[('timeout',None,None),('completed',2,1)] if timeout else [('interrupted',None,None),('completed',2,1),('completed',2,1)]
                self.assertEqual(rows,expected)
                self.assertEqual(auth.read_bytes(),b'')
            finally:
                if p.poll() is None:p.kill();p.communicate()
