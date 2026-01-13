from huggingface_hub import InferenceApi


class API:
    def __init__(self, token):
        self.inference = None
        self.token = token

    def as_model(self, repo_id):
        self.inference = InferenceApi(repo_id=repo_id, token=self.token)

    def call(self, **kwargs):
        return self.inference(**kwargs)
