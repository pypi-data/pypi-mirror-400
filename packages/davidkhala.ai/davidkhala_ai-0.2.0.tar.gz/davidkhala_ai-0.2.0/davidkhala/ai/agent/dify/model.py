from pydantic import BaseModel, Field

from davidkhala.ai.agent.dify.const import IndexingStatus


class Document(BaseModel):
    id: str
    position: int
    data_source_type: str
    data_source_info: dict[str, str]
    name: str
    indexing_status: IndexingStatus
    error: str | None
    enabled: bool


class Dataset(BaseModel):
    id: str
    name: str
    description: str


class JsonData(BaseModel):
    data: list


class NodeOutput(BaseModel):
    """Schema for Output of a Dify node"""
    text: str
    files: list
    json_: list[JsonData] = Field(alias="json") # avoid conflict with .json()
