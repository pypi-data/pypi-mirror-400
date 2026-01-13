from pydantic import BaseModel

from davidkhala.ai.agent.dify.plugins import DataSourceTypeAware


class FileModel(BaseModel):
    name: str
    size: int
    type: str
    extension: str
    mime_type: str
    transfer_method: str
    url: str
    related_id: str


class DataSourceOutput(DataSourceTypeAware):
    datasource_type:str = "local_file"
    file: FileModel
