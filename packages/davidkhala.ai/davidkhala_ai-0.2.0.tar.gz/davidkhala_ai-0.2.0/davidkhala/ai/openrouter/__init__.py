from openrouter.errors import UnauthorizedResponseError

from davidkhala.ai.model import AbstractClient
from openrouter import OpenRouter


class Client(AbstractClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenRouter(api_key)

    def chat(self, *user_prompt, **kwargs):
        r = self.client.chat.send(
            model=self.model,
            messages=[
                *self.messages,
                *[{'role': 'user', 'content': _} for _ in user_prompt]
            ]
        )
        return [_.message.content for _ in r.choices]
    def connect(self):
        try:
            self.client.models.list()
            return True
        except UnauthorizedResponseError:
            return False


class Admin:
    def __init__(self, provisioning_key: str):
        self.provisioning_key = provisioning_key
        self.client = OpenRouter(provisioning_key)
    @property
    def keys(self):
        return self.client.api_keys.list().data