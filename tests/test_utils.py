import os
import shutil
import pytest
import json
from contextlib import contextmanager
from shopify_scrape.utils import format_url, InvalidURL
from urllib.parse import ParseResult


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
                              pytest.raises(Exception)),
                             ("example.com", "not https",
                              "url", pytest.raises(Exception))
                         ]
                         )
def test_format_url_exceptions(test_input, scheme, return_type, expectation):
    with expectation:
        assert format_url(test_input, scheme, return_type) is not None


def test_save_to_file(tmp_path_factory):
    data = {'1': '1'}
    fp = os.path.join(tmp_path_factory.getbasetemp(), 'test_file.json')
    with open(fp, 'w+') as f:
        json.dump(data, f)
    assert os.path.exists(fp)