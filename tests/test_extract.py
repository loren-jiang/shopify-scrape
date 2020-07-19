from extract import get_products


def test_get_products():
    data = get_products('https://bombas.com')
    assert 'products' in data and len(data['products']) > 0
