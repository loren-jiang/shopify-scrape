import os
import requests
import json
import datetime
from urllib.parse import urlparse, ParseResult
from shopify_scrape.utils import format_url
import gzip  # gzip compresse file sizes by about factor of 10


def extract(endpoint, agg_key, page_range=None):
    r_list = []
    if page_range is not None:
        if type(page_range) != tuple:
            raise Exception("'page_range' arg must be a 'tuple' object")
        r_list = list(range(page_range[0], page_range[1]+1))
        if not r_list or (r_list[0] < 1 or r_list[-1] < 1):
            raise Exception(
                "'page_range' must be valid positive, non-zero range; e.g. (1,20)")

    page = 1
    ret = {
        agg_key: [],
        'endpoint_attempted': endpoint,
        'attempted_at': datetime.datetime.now(),
        'success': False,
        'error': ''
    }

    try:

        while True:
            page_endpoint = endpoint + f'?page={str(page)}'
            response = requests.get(page_endpoint)
            response.raise_for_status()
            if not response.headers['Content-Type'] == 'application/json; charset=utf-8':
                raise Exception('Incorrect response content type')
            data = response.json()
            page_has_products = agg_key in data and len(
                data[agg_key]) > 0

            page_in_range = page in r_list or page_range is None

            # break loop if empty or just want first page
            if not page_has_products or not page_in_range:
                break
            ret[agg_key] += data[agg_key]
            page += 1

        ret['success'] = True

    # Exception handling

    # If 4XX or 5XX status code
    except requests.exceptions.HTTPError as err:
        ret['error'] = err
    except json.decoder.JSONDecodeError as err:
        ret['error'] = err
    except Exception as err:
        ret['error'] = err

    return ret


def get_products(url, page_range=None):
    """Takes URL of Shopify store and attempts to get '/products.json' endpoint

    Args:
        url ([type]): [description]

    Returns:
        Dict: JSON data as dict
    """

    endpoint = f'{url}/products.json'
    return extract(endpoint, 'products', page_range)


def get_collections(url, page_range=None):
    """Takes URL of Shopify store and attempts to get '/products.json' endpoint

    Args:
        url ([type]): [description]

    Returns:
        Dict: JSON data as dict
    """
    endpoint = f'{url}/collections.json'
    return extract(endpoint, 'collections', page_range)


if __name__ == "__main__":
    pass
