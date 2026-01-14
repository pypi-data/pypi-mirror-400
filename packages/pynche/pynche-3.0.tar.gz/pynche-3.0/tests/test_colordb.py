from pathlib import Path

from pynche.colordb import get_colordb


def test_find_rgb_txt():
    colordb = get_colordb(('pynche.data', 'rgb.txt'))
    assert Path(colordb.filename).name == 'rgb.txt'
    assert colordb.find_byrgb((106, 90, 205)) == ('slate blue', ['SlateBlue'])
    assert colordb.find_byname('dark cyan') == (0, 139, 139)
    assert colordb.nearest(139, 200, 122) == 'palegreen3'
    assert 'gray1' in colordb.unique_names
    # This is not in unique_names because it's an alias.
    assert 'grey1' not in colordb.unique_names
    assert len(colordb.unique_names) == 502
    assert colordb.aliases_of(3, 3, 3) == ['gray1', 'grey1']
