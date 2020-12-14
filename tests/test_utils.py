import os
import pytest
import json
from contextlib import contextmanager
from shopify_scrape.utils import format_url, InvalidURL, copy_namespace, is_valid_url
from urllib.parse import ParseResult
import argparse


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize("test_input, scheme, return_type, expected",
                         [
                             ("www.example.com", "https",
                              "url", "https://www.example.com"),
                             ("example.com", "http",
                              "url", "http://example.com"),
                             ("example.com/test", "https",
                              "url", "https://example.com/test"),
                         ]
                         )
def test_format_url(test_input, scheme, return_type, expected):
    assert format_url(test_input, scheme, return_type) == expected


def test_format_url_parsed_result():
    assert type(format_url('example.com', "https",
                           "parse_result")) == ParseResult


@pytest.mark.parametrize("test_input, scheme, return_type, expectation",
                         [
                             ("bad223$$$example.com", "https",
                              "url", pytest.raises(InvalidURL)),
                             ("example.com", "https", "not url",
                              pytest.raises(ValueError)),
                             ("example.com", "not https",
                              "url", pytest.raises(ValueError))
                         ]
                         )
def test_format_url_exceptions(test_input, scheme, return_type, expectation):
    with expectation:
        assert format_url(test_input, scheme, return_type) is not None


def test_json_to_file(tmp_path_factory):
    data = {'1': '1'}
    fp = os.path.join(tmp_path_factory.getbasetemp(), 'test_file.json')
    with open(fp, 'w+') as f:
        json.dump(data, f)
    assert os.path.exists(fp)


def test_copy_namespace():
    ns1 = argparse.Namespace(**{'a': 1, 'b': 2})
    ns2 = copy_namespace(ns1)
    ns3 = copy_namespace(ns2, ['a'])

    assert ns1.a == ns2.a
    assert ns1.b == ns2.b
    assert 'b' not in vars(ns3)


@pytest.mark.parametrize("url, expectation",
                         [
                             ("$dollar.com", pytest.raises(InvalidURL)),
                             ("example.com", pytest.raises(InvalidURL)),
                             ("https://.com", pytest.raises(InvalidURL)),
                             ("https://--.hello.com", pytest.raises(InvalidURL)),
                             ("abc://--.hello.com", pytest.raises(InvalidURL)),
                         ]
                         )
def test_is_valid_url(url, expectation):
    with expectation:
        assert is_valid_url(url)
