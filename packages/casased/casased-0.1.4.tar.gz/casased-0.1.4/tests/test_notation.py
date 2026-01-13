import pytest
import casased


def test_list_assets():
    assets = casased.notation()
    assert isinstance(assets, list)
    assert 'Addoha' in assets


def test_get_isin_by_name():
    isin = casased.get_isin_by_name('Addoha')
    assert isin.startswith('MA')
    with pytest.raises(KeyError):
        casased.get_isin_by_name('UNKNOWN_ASSET')
