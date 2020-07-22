# shopify-scrape


[![CircleCI](https://circleci.com/gh/loren-jiang/misoboop.svg?style=svg)](https://circleci.com/gh/loren-jiang/shopify-scrape)
[![codecov](https://codecov.io/gh/loren-jiang/shopify-scrape/branch/master/graph/badge.svg)](https://codecov.io/gh/loren-jiang/shopify-scrape)

## Installation 
`pip install shopify_scrape`

## Usage
`python -m shopify_scrape.extract url -h`
```
usage: extract.py url [-h] [-d DEST_PATH] [-o OUTPUT_TYPE]
                      [-p PAGE_RANGE [PAGE_RANGE ...]] [-c] [-f FILE_PATH]
                      url

positional arguments:
  url                   URL to extract.

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_PATH, --dest_path DEST_PATH
                        Destination folder. Defaults to current directory
                        ('./')
  -o OUTPUT_TYPE, --output_type OUTPUT_TYPE
                        Output file type ('json' or 'csv'). Defaults to 'json'
  -p PAGE_RANGE [PAGE_RANGE ...], --page_range PAGE_RANGE [PAGE_RANGE ...]
                        Page range as tuple to extract. There are 30 items per
                        page.
  -c, --collections     If true, extracts '/collections.json' instead.
  -f FILE_PATH, --file_path FILE_PATH
                        File path to write. Defaults to
                        '[dest_path]/[url].products' or
                        '[dest_path]/[url].collections'
```

`python -m shopify_scrape.extract batch -h`
```
usage: extract.py batch [-h] [-d DEST_PATH] [-o OUTPUT_TYPE]
                        [-p PAGE_RANGE [PAGE_RANGE ...]] [-c]
                        [-r ROW_RANGE [ROW_RANGE ...]] [-l]
                        urls_file_path url_column

positional arguments:
  urls_file_path        File path of csv containing URLs to extract.
  url_column            Name of unique column with URLs.

optional arguments:
  -h, --help            show this help message and exit
  -d DEST_PATH, --dest_path DEST_PATH
                        Destination folder. Defaults to current directory
                        ('./')
  -o OUTPUT_TYPE, --output_type OUTPUT_TYPE
                        Output file type ('json' or 'csv'). Defaults to 'json'
  -p PAGE_RANGE [PAGE_RANGE ...], --page_range PAGE_RANGE [PAGE_RANGE ...]
                        Page range as tuple to extract. There are 30 items per
                        page.
  -c, --collections     If true, extracts '/collections.json' instead.
  -r ROW_RANGE [ROW_RANGE ...], --row_range ROW_RANGE [ROW_RANGE ...]
                        Row range specified as two integers.
  -l, --log             If true, logs the success of each URL attempt.
```