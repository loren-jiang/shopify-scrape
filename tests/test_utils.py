import os
import shutil
import pytest
import json
from contextlib import contextmanager
from utils import format_url, InvalidURL
from urllib.parse import ParseResult


@contextmanager
def does_not_raise():
    yield


@pytest.fixture(scope='module')
def products_dir(tmpdir_factory):
    my_tmpdir = tmpdir_factory.mktemp("products_temp")
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


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
