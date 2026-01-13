from ragflow_sdk import RAGFlow
class Client:
    def __init__(self, api_key:str, base_url ="http://localhost:9380/"):
        self.client = RAGFlow(api_key=api_key, base_url=base_url)

    @property
    def datasets(self):
        return self.client.list_datasets()