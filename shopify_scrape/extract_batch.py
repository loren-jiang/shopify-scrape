import argparse
import os
import logging
import csv
import io
from tqdm import tqdm
from datetime import datetime
from shopify_scrape.extract import main as extract
from shopify_scrape.utils import is_file_empty, copy_namespace


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


def main(args):
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

            r_range = range(args.row_range[0], args.row_range[1]+1) or range(N)
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
                data = extract(extract_args)
                if args.log:
                    logger.info(url, data.get('endpoint_attempted', ''), data.get(
                        'collected_at', ''), data.get('error', ''))


def range_arg():
    class RangeAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not len(values) == 2:
                msg = "row_range requires 2 integers"
                raise argparse.ArgumentTypeError(msg)
            try:
                values = list(map(lambda x: int(x), values))
            except ValueError:
                msg = "row_range arguments must be integers"
                raise argparse.ArgumentTypeError(msg)
            if (not values[0] > 0 and values[1] > 0) or values[0] > values[1]:
                msg = "row_range arguments must be positive integers and form a proper range (second arg is greater or equal than first arg)"
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RangeAction


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('urls_file_path', type=str,
                        help="File path of csv containing URLs to extract.")
    parser.add_argument('url_column', type=str,
                        help="Name of unique column with URLs.")
    parser.add_argument('-r', '--row_range', action=range_arg(),
                        nargs='+', help="Row range specified as two integers.")
    parser.add_argument('-d', '--dest_path', type=str,
                        help="Destination folder. Defaults to current directory ('./')", default='./')
    parser.add_argument('-o', '--output_type', type=str,
                        help="Output file type ('json' or 'csv'). Defaults to 'json'",
                        default='json')
    parser.add_argument('-c', '--collections', type=bool,
                        help="If true, extracts '/collections.json' instead.")
    parser.add_argument('-l', '--log', action='store_true',
                        help="If true, logs the success of each URL attempt.")

    args = parser.parse_args()
    main(args)
