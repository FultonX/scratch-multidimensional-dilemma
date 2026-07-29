#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
items=json.loads((root/'data/asset_manifest.json').read_text())['assets']
missing=[x['path'] for x in items if not (root/x['path']).is_file()]
if missing:
    preview='\n'.join(missing[:10])
    raise SystemExit(
        f'Missing {len(missing)} generated assets (first 10):\n{preview}\n\n'
        'Extract TheMultidirectionalDilemma-binary-assets.zip at the repository '
        'root, or run: python tools/extract_sb3.py'
    )
print(f'Validated {len(items)} logical asset references')
