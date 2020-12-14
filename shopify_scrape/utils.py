from urllib.parse import urlparse, ParseResult
import json
import re
import urllib
import os
import argparse
import contextlib
from typing import Union, Optional, List

URL_RETURN_TYPES = ("parse_result", "url")
URL_SCHEMES = ('https', 'http')
OUTPUT_TYPES = ('json', )

# Check https://regex101.com/r/A326u1/5 for reference
DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
    # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"(?:(?:(?=\S{0,253}(?:$|:))"
    # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
    r"|localhost)"  # accept also "localhost" only
    r"(:\d{1,5})?",  # port [optional]
    re.IGNORECASE
)

SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$",  # scheme: http(s) or ftp(s)
    re.IGNORECASE
)


class InvalidURL(Exception):
    pass


# def parse_csv(file_path):
#     """Given the path of a CSV file, return a list of
#         ordered dictionaries representing each row

#     Args:
#         file_path ([type]): [description]

#     Returns:
#         [type]: [description]
#     """
#     rows = []
#     with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             rows.append(row)

#     return rows


def is_valid_url(url) -> bool:
    """Returns if URL is valid (minimally has scheme and netloc)
    Taken from https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not/32171869

    Args:
        url (string): Input URL

    Returns:
        bool: Whether URL is valid
    """
    url = url.strip()

    # if not url:
    #     raise InvalidURL("No URL specified")

    # if len(url) > 2048:
    #     raise InvalidURL(
    #         f"URL exceeds its maximum length of 2048 characters (given length={len(url)})"
    #     )

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        raise InvalidURL("No URL scheme specified")
    if not re.fullmatch(SCHEME_FORMAT, scheme):
        raise InvalidURL(
            f"URL scheme must either be http(s) or ftp(s) (given scheme={scheme})")
    if not domain:
        raise InvalidURL("No URL domain specified")
    if not re.fullmatch(DOMAIN_FORMAT, domain):
        raise InvalidURL(f"URL domain malformed (domain={domain})")
    return bool(url)


def format_url(my_url, scheme='https', return_type="url"):
    """Takes input string to valid URL format

    Args:
        my_url (string): URL-like string

    Returns:
        string: Properly formatted URL
    """
    if scheme not in URL_SCHEMES:
        raise ValueError(f"'scheme' arg must be in one of {URL_SCHEMES}")
    if return_type not in URL_RETURN_TYPES:
        raise ValueError(
            f"'return_type' arg must be one of {URL_RETURN_TYPES}")

    p = urlparse(my_url, scheme=scheme)
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    p = ParseResult(scheme, netloc, path, *p[3:])
    url = p.geturl()
    if not is_valid_url(url):
        raise InvalidURL

    if return_type == 'parse_result':
        return p
    return url


def json_to_file(fp: str, data: dict):
    """Saves json data as Python dict in specified file path.

    Args:
        fp (str): File path as string.
        data (dict): Data to save.
    """
    dir_name = os.path.dirname(fp)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(fp, 'w+') as f:
        json.dump(data, f)


def is_file_empty(file_path: str) -> bool:
    """Check if file is empty by confirming if its size is 0 bytes

    Args:
        file_path (str): File path.

    Returns:
        bool: Is empty.
    """
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0


def copy_namespace(ns: argparse.Namespace,
                   attrs: Optional[List[str]] = None) -> argparse.Namespace:
    """Copies and returns new Namespace from given Namespace.
    If attrs is specified, then copies only those attrs if they exist.


    Args:
        ns (argparse.Namespace): Namespace input.
        attrs (Optional[list[str]], optional): List of attribute as strings. 
        Defaults to None.

    Returns:
        argparse.Namespace: New Namespace object.
    """
    ns_dict = vars(ns)
    if attrs is None:
        return argparse.Namespace(**ns_dict)

    ret_dict = {}
    for attr in attrs:
        ret_dict[attr] = ns_dict.get(attr)

    return argparse.Namespace(**ret_dict)


def class_as_fxn(cls):
    return cls

# Argparse validation


class RangeAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        error_msg = ''
        if not len(values) == 2:
            error_msg += "row_range requires 2 integers \n"
            raise argparse.ArgumentTypeError(error_msg)
        try:
            values = list(map(lambda x: int(x), values))
        except ValueError:
            error_msg += "row_range arguments must be integers \n"
            raise argparse.ArgumentTypeError(error_msg)
        if (not values[0] > 0 and values[1] > 0) or values[0] > values[1]:
            error_msg += "row_range arguments must be positive integers and form a proper range (second arg is greater or equal than first arg) \n"
        if error_msg:
            raise ValueError(error_msg)
        setattr(args, self.dest, values)


class FilePathAction(argparse.Action):
    def __call__(self, parser, args, value, option_string=None):
        error_msg = ''
        if re.search(r'[^A-Za-z0-9_\-\.]', value):
            error_msg += "file_path must be simple and contain only Lower/Upper Alpha, Numeric Digits, Hyphen, or Underscore"

        if error_msg:
            raise ValueError(error_msg)
        setattr(args, self.dest, value)


class ValidCsvFile(argparse.Action):
    def __call__(self, parser, args, value: str, option_string=None):
        if not value.endswith('.csv'):
            raise ValueError(
                f'Given arg for {self.dest} of {value}  must end with .csv')
        if not os.path.exists(value):
            raise ValueError(
                f"Given arg for {self.dest} of {value} does not exist.")
        if is_file_empty(value):
            raise ValueError(
                f"Given arg for {self.dest} of {value} seems to be empty.")
        setattr(args, self.dest, value)


@contextlib.contextmanager
def dummy_context_mgr():
    yield None
