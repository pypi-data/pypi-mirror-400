def test_imports():
    from tor_http import tor_http, TorHttp, TorHttpOptions
    assert tor_http is not None
    assert TorHttp is not None
    assert TorHttpOptions is not None
