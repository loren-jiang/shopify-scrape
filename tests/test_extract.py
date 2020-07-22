import pytest
import os
import requests
import argparse

from shopify_scrape.extract import extract, extract_url, parse_args, extract_batch


def test_parse_args():
    url_cli_args = parse_args(
        'url example.com -f my_path -c -o json -p 1 3'.split())
    assert url_cli_args.subparser_name == 'url'
    assert url_cli_args.url == 'example.com'
    assert url_cli_args.file_path == 'my_path'
    assert url_cli_args.collections is True
    assert url_cli_args.output_type == 'json'
    assert url_cli_args.page_range == [1, 3]

    batch_cli_args = parse_args(
        'batch urls.csv url_col -d my_dest -o csv -c'.split())
    assert batch_cli_args.subparser_name == 'batch'
    assert batch_cli_args.urls_file_path == 'urls.csv'
    assert batch_cli_args.url_column == 'url_col'
    assert batch_cli_args.collections is True
    assert batch_cli_args.output_type == 'csv'
    assert batch_cli_args.dest_path == 'my_dest'


@pytest.mark.parametrize('args_str, expectation',
                         [
                             ('url example.com -p 2 1'.split(),
                              pytest.raises(argparse.ArgumentTypeError)),
                             ('url example.com -p 0 2'.split(),
                              pytest.raises(argparse.ArgumentTypeError))
                         ]
                         )
def test_extract_url_page_range_arg_exceptions(args_str, expectation):
    with expectation:
        assert extract_url(parse_args(args_str)) is not None


def test_extract_url_with_dest_path(good_shop_domain, products_dir):
    d = str(os.path.join(products_dir, 'sub_dir'))
    args_str = f'url {good_shop_domain} -p 1 1 -d {d} -f test_file -o json'
    args = parse_args(args_str.split())
    extract_url(args)
    assert os.path.exists(os.path.join(d, 'test_file.json'))


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

    