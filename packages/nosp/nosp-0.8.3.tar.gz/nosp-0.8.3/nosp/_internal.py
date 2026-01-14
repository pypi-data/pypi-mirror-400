from typing import Union
from urllib.parse import urljoin


def _join_url(base_url, url: Union[str, list]) -> Union[list[str], str]:
    if isinstance(url, list):
        urls = []
        for i in url:
            urls.append(str(urljoin(base_url, i)))
        return urls
    if isinstance(url, str):
        return str(urljoin(base_url, url))
    return ""
