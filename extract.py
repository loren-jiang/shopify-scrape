import os
import requests
import json
from urllib.parse import urlparse, ParseResult
from utils import format_url
import gzip  # gzip compresse file sizes by about factor of 10


def get_products(url, page_range=None, use_collections=False):
    """Takes URL of Shopify store and attempts to get '/products.json' endpoint

    Args:
        url ([type]): [description]

    Returns:
        Dict: JSON data as dict
    """
    r_list = []
    if page_range is not None:
        if type(page_range) != tuple:
            raise Exception("'page_range' arg must be a 'tuple' object")
        r_list = list(range(page_range[0], page_range[0]+1))
        if not r_list or r_list[0] > 0 and r_list[-1] > 0:
            raise Exception(
                "'page_range' must be valid positive range; e.g. (1,20)")

    endpoint = f'{url}/products.json'
    page = 1
    all_products = {'products': []}

    try:

        while True:
            page_endpoint = endpoint + f'?page={str(page)}'
            response = requests.get(page_endpoint)
            response.raise_for_status()
            data = response.json()
            page_has_products = 'products' in data and len(
                data['products']) > 0

            page_in_range = page in r_list or page_range is None

            # break loop if 'products' empty or just want first page
            if not page_has_products or not page_in_range:
                break
            all_products['products'] += data['products']
            page += 1

        if use_collections:
            # TODO: implement collections when use_collections arg is True
            pass

    # Exception handling
    # TODO: handle exceptions better
    except requests.exceptions.HTTPError as err:
        print(err)
    except json.decoder.JSONDecodeError as err:
        print(err)
    except Exception as err:  # catches all Exceptions
        print(err)

    return all_products


if __name__ == "__main__":
    pass
