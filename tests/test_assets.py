import json, zipfile
from pathlib import Path

def test_manifest_references_assets_in_source_archive():
    manifest=json.loads(Path('data/asset_manifest.json').read_text())
    assert len(manifest['assets']) == 238
    with zipfile.ZipFile('source/TheMultidirectionalDilemma.sb3') as archive:
        source_files=set(archive.namelist())
    assert all(x['md5ext'] in source_files for x in manifest['assets'])
    assert all('rotation_center_x' in x for x in manifest['assets'] if x['kind']=='costume')
