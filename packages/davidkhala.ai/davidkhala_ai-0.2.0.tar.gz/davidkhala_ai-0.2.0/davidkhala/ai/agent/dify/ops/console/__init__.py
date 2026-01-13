from davidkhala.utils.http_request import Request


class API(Request):
    def __init__(self, base_url='http://localhost'):
        super().__init__()
        self.base_url = f"{base_url}/console/api"
        self.__enter__()

