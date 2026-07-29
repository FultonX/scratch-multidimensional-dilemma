import json
from pathlib import Path

def test_all_levels_and_special_mechanics_present():
    levels=json.loads(Path('data/levels.json').read_text())['levels']
    assert [x['number'] for x in levels] == list(range(1,15))
    assert [x['number'] for x in levels if 'key' in x] == [7,10,13]
    assert [x['number'] for x in levels if 'saws' in x] == [11,12,13]
    assert levels[-1]['goal'] is None

def test_dialogue_assets_are_data_driven():
    d=json.loads(Path('data/dialogue.json').read_text())['sequences']
    assert list(map(len,d.values())) == [6,4,4,6,6,4,3,3]
