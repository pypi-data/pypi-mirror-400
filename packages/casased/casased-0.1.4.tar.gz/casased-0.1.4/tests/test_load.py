import pytest
import json
import requests
import casased
from casased import load


def make_response(json_obj, status=200):
    class DummyResp:
        def __init__(self, j):
            self._j = j
            self.status_code = status
            self.text = json.dumps(j)
        def json(self):
            return self._j
        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise requests.HTTPError(f"{self.status_code} Error")
    return DummyResp(json_obj)


def test_resolve_isin():
    assert load._resolve_isin('Addoha') == 'MA0000011512'
    with pytest.raises(ValueError):
        load._resolve_isin('UNKNOWN')


def test_get_history_stock(monkeypatch):
    data = {'result':[{'Date':'2020-01-02','Value':100,'Min':90,'Max':110,'Variation':0.5,'Volume':1000},
                      {'Date':'2020-01-03','Value':101,'Min':91,'Max':111,'Variation':1.0,'Volume':1200}]}
    monkeypatch.setattr('casased.load.requests.get', lambda *args, **kwargs: make_response(data))
    df = casased.get_history('Addoha', start='2020-01-02', end='2020-01-03')
    assert df.shape[0] == 2
    assert 'Value' in df.columns


def test_get_intraday(monkeypatch):
    data = {'result':[ {'labels':['09:00','09:05'], 'data':[100,101]} ]}
    monkeypatch.setattr('casased.load.requests.get', lambda *args, **kwargs: make_response(data))
    df = casased.get_intraday('Addoha')
    # the implementation may return a raw DataFrame or a parsed one, ensure it doesn't error and is a DataFrame
    assert hasattr(df, 'columns')


def test_get_history_http_error(monkeypatch):
    # Import local modules from the repository to test the repository implementation
    import importlib.util, os
    repo_root = os.path.dirname(os.path.dirname(__file__))
    local_load_path = os.path.join(repo_root, 'casased', 'load.py')
    local_utils_path = os.path.join(repo_root, 'casased', 'utils.py')

    # Ensure the repository package is importable first
    import sys
    sys.path.insert(0, repo_root)
    try:
        # Ensure we import the repository package instead of the installed one
        for k in list(sys.modules.keys()):
            if k == 'casased' or k.startswith('casased.'):
                sys.modules.pop(k, None)
        pkg = importlib.import_module('casased')
        importlib.reload(pkg)
        local_load = importlib.import_module('casased.load')
        local_utils = importlib.import_module('casased.utils')

        def raise_http_error(*args, **kwargs):
            raise requests.HTTPError("403 Client Error: Forbidden for url")

        # Patch fetch_url in the local utils module
        monkeypatch.setattr(local_utils, 'fetch_url', raise_http_error)

        # Call the local implementation
        df = local_load.get_history('Addoha')
        assert df.empty

        with pytest.raises(requests.HTTPError):
            local_load.get_history('Addoha', raise_on_error=True)
    finally:
        # restore path
        try:
            sys.path.pop(0)
        except Exception:
            pass
