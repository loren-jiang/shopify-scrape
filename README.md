# shopify-scrape

[![CircleCI](https://circleci.com/gh/loren-jiang/misoboop.svg?style=svg)](https://circleci.com/gh/loren-jiang/shopify-scrape)
[![codecov](https://codecov.io/gh/loren-jiang/shopify-scrape/branch/master/graph/badge.svg)](https://codecov.io/gh/loren-jiang/shopify-scrape)

## Installation

`pip install shopify_scrape`

## Usage
Extracts json data for given URL.
`python -m shopify_scrape.extract url -h`

```
usage: extract.py url [-h] [-d DEST_PATH] [-p PAGE_RANGE [PAGE_RANGE ...]]
                      [-c] [-f FILE_PATH]
                      url

positional arguments:
  url                   URL to extract. An attempt will be made to fix
                        inproperly formatted URLs.

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_PATH, --dest_path DEST_PATH
                        Destination folder for extracted files. If
                        subdirectories present, they will be created if they
                        do not exist. Defaults to current directory './'
  -p PAGE_RANGE [PAGE_RANGE ...], --page_range PAGE_RANGE [PAGE_RANGE ...]
                        Inclusive page range as tuple to extract. There are 30
                        items per page. If not provided, all pages with
                        products will be taken.
  -c, --collections     If true, extracts '/collections.json' instead of
                        '/products.json'
  -f FILE_PATH, --file_path FILE_PATH
                        File path to write. Defaults to
                        '[dest_path]/[url].products' or
                        '[dest_path]/[url].collections'
```

Extracts json data for URLs given in a specified column of a csv file.
`python -m shopify_scrape.extract batch -h`

```
usage: extract.py batch [-h] [-d DEST_PATH] [-p PAGE_RANGE [PAGE_RANGE ...]]
                        [-c] [-r ROW_RANGE [ROW_RANGE ...]] [-l [LOG]]
                        urls_file_path url_column

positional arguments:
  urls_file_path        File path of csv file containing URLs to extract.
  url_column            Name of unique column with URLs.

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_PATH, --dest_path DEST_PATH
                        Destination folder for extracted files. If
                        subdirectories present, they will be created if they
                        do not exist. Defaults to current directory './'
  -p PAGE_RANGE [PAGE_RANGE ...], --page_range PAGE_RANGE [PAGE_RANGE ...]
                        Inclusive page range as tuple to extract. There are 30
                        items per page. If not provided, all pages with
                        products will be taken.
  -c, --collections     If true, extracts '/collections.json' instead of
                        '/products.json'
  -r ROW_RANGE [ROW_RANGE ...], --row_range ROW_RANGE [ROW_RANGE ...]
                        Inclusive row range specified as two integers. Should
                        be positive, with second argument greater or equal
                        than first.
  -l [LOG], --log [LOG]
                        File path of log file. If none, the log file is named
                        logs/[unix_time_in_seconds]_log.csv. 'logs' folder
                        created if it does not exist.
```
