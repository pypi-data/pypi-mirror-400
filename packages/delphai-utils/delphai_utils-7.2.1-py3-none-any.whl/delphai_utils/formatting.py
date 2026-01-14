import unicodedata
from urllib.parse import quote, unquote, urlencode

import can_ada


def normalize_url(url: str) -> str:
    """
    Transforms the raw_url with following rules:
    * Lowercase hostname
    * Lowercase schema
    * Remove default ports
    * Uppercase the percent-encoding
    * Remove trailing slashes in path
    * Remove trailing dots at end of hostnames
    * Sort query parameters:
      * sort names and then values as case sensitive strings
      * keep order of arrays ( example: "a[]=y&a[]=x" )
    * Decode international characters and UTF8
    * Normalize UTF8 with "NFKC" rules
    * percent-encode reserved characters if needed:
      * reserved characters are defined in https://datatracker.ietf.org/doc/html/rfc3986#section-2.2
      * these characters are encoded if they appear in places other than defined in https://www.rfc-editor.org/rfc/rfc3986.html
      * mainly, the path or query parts of URL are affected

    Uses can-ada url parser (https://pypi.org/project/can-ada/).
    It is compliant with the standard https://url.spec.whatwg.org/
    and  ~4x faster than urllib
    """
    parsed_url = can_ada.parse(unicodedata.normalize("NFKC", url))
    parsed_url.hostname = parsed_url.hostname.rstrip(".")
    parsed_url.pathname = quote(unquote(parsed_url.pathname)).rstrip("/")
    parsed_url.search = _normalize_url_query(parsed_url.search)
    return str(parsed_url)


def _normalize_url_query_sort_key(key_value):
    key, value = key_value
    if "[]" in key:
        return f"{key}="
    else:
        return f"{key}={value}"


def _normalize_url_query(raw_url_query: str) -> str:
    url_query = raw_url_query.lstrip("?")
    if not url_query:
        return ""
    filtered_query = [
        (key, value)
        for key, value in list(can_ada.URLSearchParams(url_query))
        if not key.startswith("utm_")
    ]
    sorted_query = sorted(filtered_query, key=_normalize_url_query_sort_key)
    return urlencode(sorted_query)


def clean_url(url, keep_www=False):
    """
    Format and clean an url to be saved or checked.
    Args:
        url: url to be formatted
        keep_www: keep the 'www' part of the url
    Returns: formatted url
    """

    url = url.strip()
    url = url.replace("https://", "").replace("http://", "").rstrip("/")
    if not keep_www:
        url = url.replace("www.", "")
    split_url = url.split("/")
    split_url[0] = split_url[0].lower()
    return "/".join(split_url)


def get_clean_domain(url):
    """
    Format and clean an url and returns domain.
    Args:
        url: url to be formatted
    Returns: formatted domain
    """

    return clean_url(url).split("/")[0]
