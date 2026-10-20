#!/usr/bin/env python3
"""Package the complete installable skill with one top-level directory."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('dist/one-minute-remotion.zip'))
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    out=a.output.expanduser().resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    allowed={'SKILL.md','README.md','LICENSE','THIRD_PARTY_NOTICES.md','agents','assets','references','scripts','examples','docs'}
    files=sorted(f for f in root.rglob('*') if f.is_file() and f.relative_to(root).parts[0] in allowed
        and not {'__pycache__','node_modules','.git'}.intersection(f.relative_to(root).parts)
        and f.suffix!='.pyc' and f.name!='.DS_Store' and not f.name.startswith('.env') and f!=out)
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        for f in files: z.write(f,Path('one-minute-remotion')/f.relative_to(root))
    with ZipFile(out) as z:
        assert z.testzip() is None
    print(f'{out}: {len(files)} files')


if __name__=='__main__': main()
