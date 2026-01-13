from pydantic import BaseModel

from davidkhala.ai.agent.dify.plugins import DataSourceTypeAware


class DataSourceInfo(BaseModel):
    source_url: str
    content: str
    title: str
    description: str


class DataSourceOutput(DataSourceTypeAware, DataSourceInfo):
    datasource_type: str = "website_crawl"


class CredentialAware(BaseModel):
    credential_id: str | None


class Console(DataSourceOutput, CredentialAware):
    pass
