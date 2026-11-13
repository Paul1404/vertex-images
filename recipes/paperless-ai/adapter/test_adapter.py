import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('paperless_ai_adapter',Path(__file__).resolve().parent/'adapter.py')
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

def valid():
    return dict(title='Test invoice',**{key:[] for key in adapter.ARRAYS})

def request():
    return {'model':adapter.MODEL,'messages':[{'role':'user','content':'Untrusted invoice data'}],
            'tools':[{'type':'function','function':{'name':'DocumentClassifierSchema','parameters':adapter.schema(True)}}]}

class PaperlessAITests(unittest.TestCase):
    def test_native_tool_request_is_accepted_without_using_supplied_schema(self):
        text,name,stream=adapter.parse_request(request())
        self.assertEqual(name,'DocumentClassifierSchema')
        self.assertFalse(stream)
        self.assertIn('Untrusted invoice data',text)

    def test_other_models_image_input_and_arbitrary_tools_are_rejected(self):
        for mutate in [lambda r:r.update(model='other'),lambda r:r['messages'][0].update(content=[{'image_url':'https://example.com'}]),lambda r:r['tools'][0]['function'].update(parameters={'properties':{'command':{}}})]:
            body=request();mutate(body)
            with self.assertRaises(ValueError):adapter.parse_request(body)

    def test_invalid_result_shapes_ids_labels_and_dates_are_rejected(self):
        for mutate in [lambda v:v.update(command='run this'),lambda v:v.update(title='x'*129),lambda v:v.update(tag_ids=[True]),lambda v:v.update(dates=['2026-02-31']),lambda v:v.update(tags=['x']*9)]:
            value=valid();mutate(value)
            with self.assertRaises(ValueError):adapter.validate(value,True)
        self.assertEqual(adapter.validate(valid(),True),valid())

    def test_model_has_no_shell_web_or_persisted_sessions(self):
        cmd=adapter.command('/tmp/schema.json')
        for flag in ['--ephemeral','--ignore-user-config','--ignore-rules','--output-schema']:self.assertIn(flag,cmd)
        self.assertIn('read-only',cmd)
        for setting in ['features.shell_tool=false','features.unified_exec=false','web_search="disabled"','history.persistence="none"']:self.assertIn(setting,cmd)
        self.assertEqual(cmd[-1],'-')

    def test_inferred_invoice_metadata_uses_the_existing_naming_convention(self):
        value=valid()
        value.update(dates=['2026-10-29'],correspondents=['Example GmbH'],document_types=['Rechnung'])
        self.assertEqual(adapter.validate(value,True)['title'],'2026-10-29_Example GmbH_Rechnung')

    def test_usage_counters_do_not_persist_document_data(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(adapter,'WORK',Path(directory)):
            adapter.record('completed',adapter.time.monotonic(),{'input_tokens':10,'output_tokens':3,'cached_input_tokens':2})
            with adapter.sqlite3.connect(Path(directory)/'usage.sqlite') as db:
                columns=[row[1] for row in db.execute('pragma table_info(requests)')]
            self.assertNotIn('content',columns)
            self.assertNotIn('document_id',columns)
            self.assertNotIn('title',columns)

    def test_failed_model_releases_capacity_without_guessing_metadata(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(adapter,'WORK',Path(directory)),patch.object(adapter.subprocess,'Popen',side_effect=RuntimeError('provider failure')),patch.object(adapter,'record'):
            (Path(directory)/'work').mkdir()
            with self.assertRaises(RuntimeError):adapter.infer('unique failed fixture',True)
            self.assertTrue(adapter.WORKER.acquire(blocking=False));adapter.WORKER.release()

    def test_parse_events_reports_real_usage_without_fabricating_it(self):
        events=[{'type':'item.completed','item':{'type':'agent_message','text':json.dumps(valid())}}, {'type':'turn.completed','usage':{'input_tokens':42,'output_tokens':8,'cached_input_tokens':2}}]
        text,usage=adapter.parse_events('\n'.join(json.dumps(x) for x in events))
        self.assertEqual(json.loads(text),valid())
        self.assertEqual(usage['input_tokens'],42)
        self.assertIsNone(adapter.parse_events('{}')[1])

if __name__=='__main__':unittest.main()
