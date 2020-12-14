import os
import requests
import json
import argparse
import sys
import csv
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urlparse
from shopify_scrape.utils import (
    format_url, json_to_file,
    RangeAction, FilePathAction,
    ValidCsvFile)
from shopify_scrape.utils import (
    copy_namespace, dummy_context_mgr)
from typing import Optional


def extract(endpoint: str, json_key: str, page_range: Optional[tuple] = None) -> list:
    """Extracts either collections or products data from specified page range.

    Args:
        endpoint (str): Endpoint to extract.
        json_key (str): 'collections' or 'products'
        page_range (Optional[tuple], optional): Tuple of page range (start, end). 
        Defaults to None.

    Raises:
        ValueError: Incorrect response content type.

    Returns:
        list: Aggregated data from source url's pages.
    """
    r_list = list(range(page_range[0], page_range[1]+1)) if page_range else []
    page = 1
    agg_data = []

    while True:
        page_endpoint = endpoint + f'?page={str(page)}'
        response = requests.get(page_endpoint, timeout=(
            int(os.environ.get('REQUEST_TIMEOUT', 0)) or 10))
        response.raise_for_status()
        if response.url != page_endpoint:  # to handle potential redirects
            p_endpoint = urlparse(response.url)  # parsed URL
            endpoint = (p_endpoint.scheme + '://' +
                        p_endpoint.netloc + p_endpoint.path)
        if not response.headers['Content-Type'] == 'application/json; charset=utf-8':
            raise ValueError('Incorrect response content type')
        data = response.json()
        page_has_products = json_key in data and len(
            data[json_key]) > 0

        page_in_range = page in r_list or page_range is None

        # break loop if empty or want first page
        if not page_has_products or not page_in_range:
            break
        agg_data.extend(data[json_key])
        page += 1
    return agg_data


def extract_url(args: argparse.Namespace) -> dict:
    """Extracts data from products.json endpoint from specified args.

    Args:
        args (argparse.Namespace): Parsed args.

    Returns:
        dict: Data logged from extraction, including if successful 
        or errors present.
    """
    p = format_url(args.url, scheme='https', return_type='parse_result')

    formatted_url = p.geturl()
    json_key = 'products'
    if args.collections:
        json_key = 'collections'
    fp = os.path.join(
        args.dest_path, f'{p.netloc}.{json_key}.json')

    if args.file_path:
        fp = os.path.join(
            args.dest_path, f'{args.file_path}.json')

    endpoint = f'{formatted_url}/{json_key}.json'
    ret = {
        'url': endpoint,
        'collected_at': str(datetime.now()),
        'success': False,
        'error': '',
        'file_path': '',
    }
    try:
        data = extract(endpoint, json_key, args.page_range)

    except requests.exceptions.HTTPError as err:
        ret['error'] = str(err)
    except json.decoder.JSONDecodeError as err:
        ret['error'] = str(err)
    except Exception as err:
        ret['error'] = str(err)
    else:
        ret['success'] = True
        ret[json_key] = data

    if ret['success']:
        ret['file_path'] = fp
        json_to_file(fp, data)
    return ret


def extract_batch(args: argparse.Namespace) -> list:
    """Extracts multiple URLs given in csv file.

    Args:
        args (argparse.Namespace): Parsed args.

    Raises:
        ValueError: Given url column name is not in csv file's first row.
        ValueError: Given row range is not within number of rows in csv file provided.

    Returns:
        list: List of extraction results (same as extract_url).
    """

    if not os.path.exists(args.dest_path):
        os.mkdir(args.dest_path)

    if args.log:
        log_dir = os.path.dirname(args.log)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    with open(args.urls_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        rows = list(reader)

    N = len(rows)
    first_row = rows[0]
    try:
        url_column_idx = first_row.index(args.url_column)
    except ValueError:
        raise ValueError('url_column',
                                     f"{args.url_column} is not in the csv file's first row.")

    r_range = range(1, N)
    if args.row_range:
        r_range = range(args.row_range[0], args.row_range[1]+1)

    r_range_list = list(r_range)

    if r_range_list[-1] > N:
        raise ValueError('row_range',
                                     f"Given row_range {r_range} is not within the number of rows in csv file.")

    row_results = []
    with open(args.log, 'w', newline='') if args.log else dummy_context_mgr() as log_file:
        writer = csv.writer(log_file, delimiter=',')if log_file else None
        for i in tqdm(r_range_list):
            row = rows[i]
            url = row[url_column_idx]
            extract_args = copy_namespace(
                args, ['collections', 'page_range', 'dest_path', 'file_path'])
            extract_args.url = url
            data = extract_url(extract_args)
            row_results.append(data)
            if writer:
                data_row = [url, data.get('url', ''), data.get(
                    'collected_at', ''), data.get('error', ''),
                    data.get('file_path', '')]
                writer.writerow(data_row)
    return row_results


def parse_args(argv=sys.argv[1:]):
    # shared args
    # dest_path, page_range, collections
    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument('-d', '--dest_path', type=str,
                               help="""Destination folder for extracted files. 
                               If subdirectories present, they will be created
                               if they do not exist.
                               Defaults to current directory './'""",
                               default='./')
    parent_parser.add_argument('-p', '--page_range',
                               action=RangeAction, nargs='+',
                               help="""Inclusive page range as tuple to extract. 
                               There are 30 items per page. If not provided, 
                               all pages with products will be taken.""")
    parent_parser.add_argument('-c', '--collections', action='store_true',
                               help="""If true, extracts '/collections.json' 
                               instead of '/products.json'""")

    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="subparser_name")

    # for url subcommand
    url_parser = subparsers.add_parser('url', parents=[parent_parser])
    url_parser.add_argument('url', type=str,
                            help="""URL to extract. An attempt will be made to 
                            fix inproperly formatted URLs.""")
    url_parser.add_argument('-f', '--file_path', type=str,
                            action=FilePathAction,
                            help="""File path to write. Defaults to 
                            '[dest_path]/[url].products' or 
                            '[dest_path]/[url].collections'""")

    # for batch subcommand
    batch_parser = subparsers.add_parser('batch', parents=[parent_parser])
    batch_parser.add_argument('urls_file_path', type=str,
                              action=ValidCsvFile,
                              help="""File path of csv file containing 
                              URLs to extract.""")
    batch_parser.add_argument('url_column', type=str,
                              help="""Name of unique column with URLs.""")
    batch_parser.add_argument('-r', '--row_range', action=RangeAction,
                              nargs='+',
                              help="""Inclusive row range specified as two integers.
                              Should be positive, with second argument greater or equal
                              than first.""")
    batch_parser.add_argument('-l', '--log',
                              nargs='?', type=str,
                              const=f"logs/{str(round(datetime.now().timestamp()))}_log.csv",
                              help="""File path of log file. If none, the log file 
                              is named logs/[unix_time_in_seconds]_log.csv.
                              'logs' folder created if it does not exist.""")

    return parser.parse_args(args=argv)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if args.subparser_name == 'url':
        extract_url(args)
    elif args.subparser_name == 'batch':
        extract_batch(args)
