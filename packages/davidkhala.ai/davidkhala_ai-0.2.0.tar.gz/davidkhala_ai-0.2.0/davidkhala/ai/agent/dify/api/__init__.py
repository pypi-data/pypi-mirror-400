from typing import Iterable, Callable, Any, Optional

from davidkhala.utils.http_request import Request


class API(Request):
    def __init__(self, api_key: str, base_url="https://api.dify.ai/v1"):
        super().__init__({'bearer': api_key})
        self.base_url = base_url
        self.api_key = api_key


class Iterator(Iterable):
    def __iter__(self):
        return self

    def __init__(self, get_fn: Callable[[int, int], Any], r: Optional[dict]):
        self.response = r
        self.fn = get_fn

    def __next__(self):
        if self.response and not self.response['has_more']:
            raise StopIteration
        page = 1 if not self.response else self.response['page'] + 1
        limit = None if not self.response else self.response['limit']
        self.response = self.fn(page, limit)
        return self.response['data']
