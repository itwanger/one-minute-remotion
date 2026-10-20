"""Import one user-supplied audio file per beat without changing speed or recording any credentials."""
import argparse
from pathlib import Path
import shutil
import subprocess
from project_paths import project_path, load_config, load_beats, read_json, write_json, sha256, request_hash


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',required=True,type=project_path)
    p.add_argument('--id',required=True,type=int)
    p.add_argument('--audio',required=True,type=Path)
    p.add_argument('--replace',action='store_true',help='Replace only an explicitly authorized audio revision')
    a=p.parse_args()
    cfg=load_config(a.project)
    if not cfg['tts'].get('speakerId'): p.error('Set a descriptive ID for your chosen voice in project.json before importing')
    if cfg['tts'].get('atempo',1)!=1: p.error('Imported audio is already at its chosen speed; set atempo=1 before locking')
    _,beats=load_beats(a.project)
    matches=[b for b in beats if b['id']==a.id]
    if not matches: p.error('Unknown beat ID')
    source=a.audio.expanduser().resolve()
    if not source.is_file(): p.error('Audio file missing')
    # Store a lossless decoded WAV; do not introduce MP3 encoder padding between imported beats.
    dest=a.project/'audio/processed'/f'beat_{a.id:02d}.wav'
    if any(dest.parent.glob(f'beat_{a.id:02d}.*')) and not a.replace: p.error('Audio exists; preserve it before an authorized --replace')
    if not shutil.which('ffmpeg'): p.error('ffmpeg is required')
    tmp=dest.with_suffix('.tmp.wav')
    try:
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar',str(cfg['tts']['audio']['sampleRate']),'-ac','1','-c:a','pcm_s16le',str(tmp)],check=True)
        tmp.replace(dest)
    finally: tmp.unlink(missing_ok=True)
    if a.replace:
        for other in dest.parent.glob(f'beat_{a.id:02d}.*'):
            if other!=dest: other.unlink()
    record=a.project/'build/audio-generation.json'
    records=read_json(record) if record.exists() else {'units':{}}
    b=matches[0]
    records['units'][str(a.id)]={'requestHash':request_hash(b.get('ttsText') or b['text'],cfg['tts']),
        'processedSha256':sha256(dest),'atempo':1,'importedSourceSha256':sha256(source),'source':'user-supplied audio; identity and transcription need review'}
    write_json(record,records)
    print(f'Imported beat {a.id}; no TTS call. Run gen_cues.py after all beats are imported.')


if __name__=='__main__': main()
