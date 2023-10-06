from urllib.parse import urlparse
from validators import url


def validate_url(input_url):
    return True if url(input_url) else False


def normalize_url(input_url):
    url = urlparse(input_url)
    return f'{url.scheme}://{url.netloc}'
