import pytest
from shopify_scrape.extract import get_products, get_collections, main

def test_main(tmp_path_factory):
    fp = os.path.join(tmp_path_factory.getbasetemp(), 'test_file.json')


def test_get_products():
    data = get_products('https://bombas.com')
    assert 'products' in data and len(data['products']) > 0

def test_get_products_with_page_range():
    data = get_products('https://bombas.com', page_range=(1, 2))
    assert 'products' in data and len(data['products']) == 60

@pytest.mark.parametrize("test_url, page_range, expectation",
                         [
                             ('https://bombas.com', (-1, 3),
                              pytest.raises(Exception)),
                              ('https://bombas.com', (3, 1),
                              pytest.raises(Exception))
                         ]
                         )
def test_get_products_page_range_exceptions(test_url, page_range, expectation):
    with expectation:
        assert get_products(test_url, page_range) is not None

def test_get_products_bad_url():
    data = get_products('https://google.com')
    assert data['success'] == False, "Unsuccessful 'products.json' retrieval"

def test_get_collections():
    data = get_collections('https://bombas.com')
    assert 'collections' in data and len(data['collections']) > 0
