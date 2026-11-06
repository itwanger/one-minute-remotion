"""Create a portable video project; never overwrite, synthesize, or install dependencies."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
from project_paths import SHARED, write_json, link_public


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', required=True, type=Path)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--spoken', type=Path, help='Explicitly extracted plain narration; no automatic Markdown extraction')
    p.add_argument('--config', type=Path, help='Your own config, never a bundled private voice')
    p.add_argument('--title')
    a = p.parse_args()
    project, source = a.project.expanduser().resolve(), a.source.expanduser().resolve()
    if project.exists():
        p.error('Project exists; inspect and continue it instead of overwriting')
    if not source.is_file() or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', project.name):
        p.error('Need an existing source and a lowercase-hyphenated project directory name')
    collection = next((parent for parent in project.parents if parent.name == 'one-minute'), None)
    if collection:
        layout = project.relative_to(collection).parts
        if layout and layout[0] == '_archive': layout = layout[1:]
        if len(layout) != 3 or layout[0] == 'shared' or not all(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', part) for part in layout):
            p.error('Collection projects use one-minute/<topic>/<tool>/<variant>')
    cfg = json.loads((a.config.expanduser() if a.config else SHARED/'config/video.config.json').read_text())
    for k in ('tts','video','volc'):
        if k not in cfg: p.error('Config needs tts, video and volc sections')
    if not isinstance(cfg['video']['fps'], int) or cfg['video']['fps'] <= 0:
        p.error('FPS must be a positive integer')
    narration = a.spoken.expanduser().read_text() if a.spoken else None
    if narration is not None and not narration.strip(): p.error('Narration is empty')
    palette = json.loads((SHARED.parents[1]/'palette.json').read_text())
    palettes = {
        'palette-v1.ts': ('palette.ts', 'C', '// Default palette provenance: installed skill assets/palette.json\nexport const C = '+json.dumps(palette['C'],indent=2)+' as const;\n'),
        'memphis-v1.ts': ('memphis-palette.ts', 'MEMPHIS', (SHARED.parents[1]/'styles/memphis-palette.ts').read_text()),
    }
    if collection:
        for name, (_, _, text) in palettes.items():
            shared = collection/'shared/styles'/name
            if shared.exists() and shared.read_text() != text:
                p.error(f'Shared palette differs; preserve it and choose a new version explicitly: {shared}')
    for d in ('assets/references','assets/images','audio/raw','audio/processed','build','preview','output'):
        (project/d).mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, project/'script.md')
    title = a.title or project.name
    meta = {'schemaVersion':1, 'slug':project.name, 'title':title,
            'compositionId': 'OneMinuteVideo', 'outputName':project.name+'.mp4',
            'sourceArticle': str(source), 'config':cfg}
    write_json(project/'project.json', meta)
    beats = []
    if narration is not None:
        (project/'spoken.txt').write_text(narration)
        beats = [{'id':1, 'chapter':'ch1', 'text':narration.replace('\r','').replace('\n','')}]
    write_json(project/'beats.json', {'chapters':[{'id':'ch1','title':title}] if beats else [],'beats':beats})
    shutil.copytree(SHARED/'remotion/templates', project/'remotion')
    link_public(project)
    (project/'build/cues.ts').write_text('export const TOTAL_FRAMES = 90;\nexport const CUES: {text:string; startFrame:number; durationFrames:number}[] = [];\n')
    for name, (local_name, exported, text) in palettes.items():
        local = project/'remotion/src'/local_name
        if collection:
            shared = collection/'shared/styles'/name
            shared.parent.mkdir(parents=True, exist_ok=True)
            if not shared.exists(): shared.write_text(text)
            relative = os.path.relpath(shared.with_suffix(''), local.parent).replace(os.sep, '/')
            local.write_text(f'// Shared frozen base; keep topic-specific overrides local.\nexport {{{exported}}} from {relative!r};\n')
        else:
            local.write_text(text)
    (project/'PROGRESS.md').write_text('# 制作进度\n\n已创建工程，尚未生成配音或完成视频。\n')
    print(json.dumps({'project':str(project),'status':'initialized; no TTS, npm install or rendering executed','voiceConfigured':bool(cfg['tts'].get('speakerId'))},ensure_ascii=False))


if __name__ == '__main__':
    main()
