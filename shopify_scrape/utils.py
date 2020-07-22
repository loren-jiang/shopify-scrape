from urllib.parse import urlparse, ParseResult
import csv
import json
import re
import urllib
import os
import argparse
import contextlib

URL_RETURN_TYPES = ("parse_result", "url")
URL_SCHEMES = ('https', 'http')
OUTPUT_TYPES = ('json', 'csv')

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


def is_valid_url(url):
    """Returns if URL is valid (minimally has scheme and netloc)
    Taken from https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not/32171869

    Args:
        url (String): Input URL

    Returns:
        Boolean: Whether URL is valid
    """
    url = url.strip()

    if not url:
        raise InvalidURL("No URL specified")

    if len(url) > 2048:
        raise InvalidURL(
            "URL exceeds its maximum length of 2048 characters (given length={})".format(len(url)))

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        raise InvalidURL("No URL scheme specified")
    if not re.fullmatch(SCHEME_FORMAT, scheme):
        raise InvalidURL(
            "URL scheme must either be http(s) or ftp(s) (given scheme={})".format(scheme))
    if not domain:
        raise InvalidURL("No URL domain specified")
    if not re.fullmatch(DOMAIN_FORMAT, domain):
        raise InvalidURL("URL domain malformed (domain={})".format(domain))
    return bool(url)


def format_url(my_url, scheme='https', return_type="url"):
    """Takes input string to valid URL format

    Args:
        my_url (String): URL-like string

    Returns:
        String: Properly formatted URL
    """
    if scheme not in URL_SCHEMES:
        raise Exception(f"'scheme' arg must be in one of {URL_SCHEMES}")
    if return_type not in URL_RETURN_TYPES:
        raise Exception(f"'return_type' arg must be one of {URL_RETURN_TYPES}")

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

def save_to_file(fp, data, output_type='json'):
    print(fp)
    if output_type not in OUTPUT_TYPES:
        raise Exception(f"'output_type' arg must be in one of {OUTPUT_TYPES}")
    dir_name = os.path.dirname(fp)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(fp, 'w+') as f:
        if output_type == 'json':
            json.dump(data, f)
        elif output_type == 'csv':
            #TODO: write this case
            pass

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0

def copy_namespace(ns, attrs=None):
    """Returns shallow copy of Namespace ns. If attrs is specified, then copies those attrs if they exist.

    Args:
        ns ([type]): [description]
        attrs ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    ns_dict = vars(ns)
    if attrs is None:
        return argparse.Namespace(**ns_dict)

    ret_dict = {}
    for attr in attrs:
        ret_dict[attr] = ns_dict.get(attr)

    return argparse.Namespace(**ret_dict)
    
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



@contextlib.contextmanager
def dummy_context_mgr():
    yield None