import os
import requests
import json
import datetime
import argparse
from urllib.parse import urlparse, ParseResult
from shopify_scrape.utils import format_url, save_to_file
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
        'collected_at': str(datetime.datetime.now()),
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
        url (String): URL to extract

    Returns:
        Dict: JSON data as dict
    """

    endpoint = f'{url}/products.json'
    return extract(endpoint, 'products', page_range)


def get_collections(url, page_range=None):
    """Takes URL of Shopify store and attempts to get '/collections.json' endpoint

    Args:
        url (String): URL to extract

    Returns:
        Dict: JSON data as dict
    """
    endpoint = f'{url}/collections.json'
    return extract(endpoint, 'collections', page_range)


def main(args):

    # url, collections, file_path, page_range, output_type
    url = args.url
    collections = args.collections
    file_path = args.file_path
    page_range = args.page_range
    output_type = args.output_type
    dest_path = args.dest_path

    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    p = format_url(url, scheme='https', return_type='parse_result')
    formatted_url = p.geturl()
    fp = os.path.join(dest_path, f'{p.netloc}.products.{output_type}')
    page_range = None

    if collections:
        fp = os.path.join(dest_path, f'{formatted_url}.collections.{output_type}')
    if file_path:
        fp = file_path
    if page_range:
        page_range = page_range

    if collections:
        data = get_collections(formatted_url, page_range)
    else:
        data = get_products(formatted_url, page_range)
    if data['success']:
        save_to_file(fp, data, output_type)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('url', type=str, help="URL to extract.")
    parser.add_argument('-d', '--dest_path', type=str,
                        help="Destination folder. Defaults to current directory ('./')", default='./')
    parser.add_argument('-f', '--file_path', type=str,
                        help="File path to write. Defaults to '[dest_path]/[url].products' or '[dest_path]/[url].collections'")
    parser.add_argument('-o', '--output_type', type=str,
                        help="Output file type ('json' or 'csv'). Defaults to 'json'",
                        default='json')
    parser.add_argument('-p', '--page_range', type=tuple,
                        help="Page range as tuple to extract. There are 30 items per page.")
    parser.add_argument('-c', '--collections', action='store_true',
                        help="If true, extracts '/collections.json' instead.")

    args = parser.parse_args()
    # main(args.url, args.collections, args.file_path, args.page_rage, args.output_type)
    main(args)
