import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'assets/runtime/shared/tools'


def run(script,*args):
    return subprocess.run([sys.executable,str(script),*map(str,args)],capture_output=True,text=True)


class PackageTests(unittest.TestCase):
    def test_vendor_integrity_and_complete_zip(self):
        vendor=ROOT/'assets/huashu'
        for name,sha in json.loads((vendor/'provenance.json').read_text())['sha256'].items():
            self.assertEqual(hashlib.sha256((vendor/name).read_bytes()).hexdigest(),sha,name)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'skill.zip'
            self.assertEqual(run(ROOT/'scripts/package_skill.py','--output',out).returncode,0)
            with ZipFile(out) as z:
                self.assertIsNone(z.testzip())
                for name in ['SKILL.md','LICENSE','assets/runtime/shared/tools/import_audio.py','assets/huashu/diagram.js','references/motion.md']:
                    self.assertIn('one-minute-remotion/'+name,z.namelist())
                self.assertFalse(any('node_modules/' in n or '__pycache__/' in n or '/.env' in n for n in z.namelist()))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.source=self.folder/'rrf.md'
        self.source.write_text('第一段。\n第二段。')
        self.spoken=self.folder/'spoken.txt'
        self.spoken.write_bytes(self.source.read_bytes())
        self.project=self.folder/'one-minute-test'
        result=run(TOOLS/'init_project.py','--project',self.project,'--source',self.source,'--spoken',self.spoken)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_no_private_voice_and_no_overwrite(self):
        meta=json.loads((self.project/'project.json').read_text())
        self.assertEqual(meta['config']['tts']['speakerId'],'')
        self.assertEqual((self.project/'script.md').read_bytes(),self.source.read_bytes())
        self.assertFalse((self.project/'build/voiceover.wav').exists())
        result=run(TOOLS/'init_project.py','--project',self.project,'--source',self.source)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.project/'script.md').read_bytes(),self.source.read_bytes())
        result=run(ROOT/'scripts/one_minute.py','lock','--project',self.project,'--source',self.source,'--spoken',self.project/'spoken.txt')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('speakerId',result.stdout)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'Requires FFmpeg')
    def test_full_narration_import_duration_and_mutation_guards(self):
        meta_path=self.project/'project.json'
        meta=json.loads(meta_path.read_text())
        meta['config']['tts']['speakerId']='user-provided-test-audio'
        meta_path.write_text(json.dumps(meta))
        (self.project/'beats.json').write_text(json.dumps({'chapters':[{'id':'ch1','title':'test'}],
            'beats':[{'id':1,'chapter':'ch1','text':'第一段。'},{'id':2,'chapter':'ch1','text':'第二段。'}]}))
        locked=run(ROOT/'scripts/one_minute.py','lock','--project',self.project,'--source',self.source,'--spoken',self.project/'spoken.txt')
        self.assertEqual(locked.returncode,0,locked.stdout)
        audio=self.folder/'input.wav'
        with wave.open(str(audio),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000)
            # Synthetic test signal, never a distributed voice sample.
            w.writeframes((b'\x80\x01\x80\xfe'*390000))
        for beat in (1,2):
            result=run(TOOLS/'import_audio.py','--project',self.project,'--id',beat,'--audio',audio)
            self.assertEqual(result.returncode,0,result.stderr)
        result=run(TOOLS/'import_audio.py','--project',self.project,'--id',1,'--audio',audio)
        self.assertNotEqual(result.returncode,0)
        result=run(TOOLS/'gen_cues.py','--project',self.project)
        self.assertEqual(result.returncode,0,result.stderr)
        result=run(ROOT/'scripts/one_minute.py','check','--project',self.project)
        report=json.loads(result.stdout)
        self.assertEqual(result.returncode,0,result.stdout)
        self.assertAlmostEqual(report['audioDurationSec'],65)
        self.assertTrue(report['warnings'])
        self.assertAlmostEqual(report['overTargetSec']['audioDurationSec'],5)
        self.assertEqual(self.source.read_text(),'第一段。\n第二段。')
        self.source.write_text('改过的稿件。')
        result=run(ROOT/'scripts/one_minute.py','check','--project',self.project)
        self.assertEqual(result.returncode,1)
        self.assertIn('source changed',result.stdout)
        self.source.write_text('第一段。\n第二段。')
        meta['config']['tts']['speakerId']='another-voice'
        meta_path.write_text(json.dumps(meta))
        result=run(ROOT/'scripts/one_minute.py','check','--project',self.project)
        self.assertEqual(result.returncode,1)
        self.assertIn('Voice or playback settings changed',result.stdout)


if __name__=='__main__': unittest.main()
