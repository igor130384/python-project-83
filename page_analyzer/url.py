from urllib.parse import urlparse


def pars_url(data: str):
    url_parse = urlparse(data)
    return f"{url_parse.scheme}://{url_parse.netloc}"
