import pytest
import os
import argparse

from shopify_scrape.extract import (
    extract, extract_url, parse_args, extract_batch)


@pytest.mark.parametrize('args_str, expectation',
                         [
                             ('url example.com -p 2 1'.split(),
                              pytest.raises(ValueError)),
                             ('url example.com -p 0 2'.split(),
                              pytest.raises(ValueError)),
                             ('url example.com -p 0'.split(),
                              pytest.raises(argparse.ArgumentTypeError)),
                             ('url example.com -p h a'.split(),
                              pytest.raises(argparse.ArgumentTypeError)),
                             ('url example.com -f bad_fp$ -p 0 1'.split(),
                              pytest.raises(ValueError))
                         ]
                         )
def test_extract_url_args(args_str, expectation):
    with expectation:
        assert extract_url(parse_args(args_str)) is not None


def test_extract_url_with_dest_path(good_shop_domain, products_dir):
    d = str(os.path.join(products_dir, 'sub_dir'))
    fp = 'test_file.products'
    args_str = f'url {good_shop_domain} -p 1 1 -d {d} -f {fp}'
    args = parse_args(args_str.split())
    extract_url(args)
    assert os.path.exists(os.path.join(d, f'{fp}.json'))


def test_extract_products():
    products = extract('https://bombas.com/products.json', 'products')
    assert len(products) > 0


def test_extract_products_with_page_range():
    products = extract('https://bombas.com/products.json',
                       'products', page_range=(1, 2))
    assert len(products) == 60


@pytest.mark.parametrize("args",
                         [
                             ('url google.com'.split()),
                         ]
                         )
def test_extract_products_bad_urls(args):
    args = parse_args(args)
    data = extract_url(args)
    assert data['success'] is False


def test_extract_collections():
    collections = extract('https://bombas.com/collections.json', 'collections')
    assert len(collections) > 0


def test_extract_batch(products_dir):
    args_str = f'batch examples/urls.csv urls -l logs/pytest_log.csv -d {products_dir} -p 1 1'
    args = parse_args(args_str.split())
    extract_batch(args)
    assert os.path.exists('logs/pytest_log.csv')


@pytest.mark.parametrize('args_str, expectation',
                         [
                             ('batch examples/urls.csv col_not_in_file -p 1 1'.split(),
                              pytest.raises(ValueError)),
                             ('batch examples/not_file.csv col_not_in_file -p 1 1'.split(),
                              pytest.raises(ValueError)),
                         ]
                         )
def test_extract_batch_args(args_str, expectation):
    with expectation:
        extract_batch(parse_args(args_str))
