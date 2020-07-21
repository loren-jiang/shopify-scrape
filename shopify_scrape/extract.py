import os
import requests
import json
from datetime import datetime
import logging
import argparse
from tqdm import tqdm
import io
import csv
from urllib.parse import urlparse
from shopify_scrape.utils import format_url, save_to_file, range_arg
from shopify_scrape.utils import copy_namespace, is_file_empty
# import gzip  # gzip compresse file sizes by about factor of 10


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
        'collected_at': str(datetime.now()),
        'success': False,
        'error': ''
    }

    try:

        while True:
            page_endpoint = endpoint + f'?page={str(page)}'
            response = requests.get(page_endpoint, timeout=10)
            response.raise_for_status()
            if response.url != page_endpoint:  # to handle potential redirects            
                p_endpoint = urlparse(response.url)  # parsed URL
                endpoint = p_endpoint.scheme + '://' + p_endpoint.netloc + p_endpoint.path
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


def extract_url(url, collections, file_path, page_range,
                output_type, dest_path, *args, **kwargs):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    p = format_url(url, scheme='https', return_type='parse_result')
    formatted_url = p.geturl()
    fp = os.path.join(dest_path, f'{p.netloc}.products.{output_type}')
    page_range = None

    if collections:
        fp = os.path.join(
            dest_path, f'{formatted_url}.collections.{output_type}')
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


def main(namespace):
    namespace_dict = vars(namespace)
    if namespace.subparser_name == 'url':
        extract_url(**namespace_dict)

    if namespace.subparser_name == 'batch':
        extract_batch(namespace)


def extract_batch(args):
    if args:
        if not os.path.exists(args.urls_file_path):
            raise Exception(f"{args.urls_file_path} does not exist.")
        if not args.urls_file_path.endswith('.csv'):
            raise Exception(f"Must be .csv file.")
        if is_file_empty(args.urls_file_path):
            raise Exception(f"{args.urls_file_path} seems to be empty.")

        if not os.path.exists(args.dest_path):
            os.mkdir(args.dest_path)

        if args.log:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            now = datetime.now()
            seconds_since_epoch = round(datetime.now().timestamp())
            log_filename = f"logs/{str(seconds_since_epoch)}_log.csv"
            logging.basicConfig(filename=log_filename, level=logging.INFO)
            logger = logging.getLogger(__name__)
            logging.root.handlers[0].setFormatter(CsvFormatter())
            logger.info(f'Batch extraction started at {str(now)}')
            logger.info('url', 'collected_at', 'output_file', 'error')

        with open(args.urls_file_path, 'r+') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
            N = len(rows)
            first_row = rows[0]
            url_column_idx = first_row.index(args.url_column)

            if url_column_idx == -1:
                raise Exception(
                    f"{args.url_column} is not in the csv file's first row.")

            r_range = range(1, N)
            if args.row_range:
                r_range = range(args.row_range[0], args.row_range[1]+1)

            r_range_list = list(r_range)

            if r_range_list[-1] > N:
                raise Exception(
                    f"Given row_range {r_range} is not within the number of rows in csv file.")

            for i in tqdm(r_range_list):
                row = rows[i]
                url = row[url_column_idx]
                extract_args = copy_namespace(
                    args, ['collections', 'output_type', 'page_range', 'dest_path', 'file_path'])
                extract_args.url = url
                data = extract_url(**vars(extract_args))
                if args.log:
                    logger.info(url, data.get('endpoint_attempted', ''), data.get(
                        'collected_at', ''), data.get('error', ''))


class CsvFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    def format(self, record):
        self.writer.writerow([record.levelname, record.msg] +
                             list(map(lambda x: str(x), record.args)))
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()


if __name__ == "__main__":
    # shared args
    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument('-d', '--dest_path', type=str,
                               help="Destination folder. Defaults to current directory ('./')", default='./')

    parent_parser.add_argument('-o', '--output_type', type=str,
                               help="Output file type ('json' or 'csv'). Defaults to 'json'",
                               default='json')
    parent_parser.add_argument('-p', '--page_range', action=range_arg(), nargs='+',
                               help="Page range as tuple to extract. There are 30 items per page.")
    parent_parser.add_argument('-c', '--collections', action='store_true',
                               help="If true, extracts '/collections.json' instead.")

    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="subparser_name")

    # for url command
    url_parser = subparsers.add_parser('url', parents=[parent_parser])
    url_parser.add_argument('url', type=str, help="URL to extract.")
    url_parser.add_argument('-f', '--file_path', type=str,
                            help="File path to write. Defaults to '[dest_path]/[url].products' or '[dest_path]/[url].collections'")

    # for batch command
    batch_parser = subparsers.add_parser('batch', parents=[parent_parser])
    batch_parser.add_argument('urls_file_path', type=str,
                              help="File path of csv containing URLs to extract.")
    batch_parser.add_argument('url_column', type=str,
                              help="Name of unique column with URLs.")
    batch_parser.add_argument('-r', '--row_range', action=range_arg(),
                              nargs='+', help="Row range specified as two integers.")
    batch_parser.add_argument('-l', '--log', action='store_true',
                              help="If true, logs the success of each URL attempt.")

    args = parser.parse_args()
    main(args)
