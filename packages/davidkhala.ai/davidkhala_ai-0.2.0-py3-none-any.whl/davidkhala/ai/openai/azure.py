from davidkhala.utils.syntax.compat import deprecated
from openai import AzureOpenAI, OpenAI

from davidkhala.ai.openai import Client


class AzureHosted(Client):
    def chat(self, *user_prompt, **kwargs):
        if 'web_search_options' in kwargs:
            raise ValueError('Web search options not supported in any models of Azure AI Foundry')
        return super().chat(*user_prompt, **kwargs)

class ModelDeploymentClient(AzureHosted):
    def __init__(self, key, deployment):
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",  # mandatory
            azure_endpoint=f"https://{deployment}.cognitiveservices.azure.com/",
            api_key=key,
        )


@deprecated("Azure Open AI is deprecated. Please migrate to Microsoft Foundry")
class OpenAIClient(AzureHosted):

    def __init__(self, api_key, project):
        self.client = OpenAI(
            base_url=f"https://{project}.openai.azure.com/openai/v1/",
            api_key=api_key,
        )

    def as_chat(self, model="gpt-oss-120b", sys_prompt: str = None):
        super().as_chat(model, sys_prompt)
