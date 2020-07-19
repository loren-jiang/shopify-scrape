from urllib.parse import urlparse, ParseResult
import csv
import re
import urllib


class InvalidURL(Exception):
    pass


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

URL_RETURN_TYPES = ("parse_result", "url")
URL_SCHEMES = ('https', 'http')

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
