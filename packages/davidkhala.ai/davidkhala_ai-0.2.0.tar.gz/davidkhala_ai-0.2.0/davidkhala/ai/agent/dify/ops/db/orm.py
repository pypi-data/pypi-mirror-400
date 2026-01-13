import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DifyBase(Base):
    __abstract__ = True  # keyword for SQLAlchemy
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())


class AppModelConfig(DifyBase):
    __tablename__ = "app_model_configs"
    __table_args__ = {"schema": "public"}

    app_id = Column(UUID(as_uuid=True), nullable=False)

    provider = Column(String(255))
    model_id = Column(String(255))
    configs = Column(JSON)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    opening_statement = Column(Text)
    suggested_questions = Column(Text)
    suggested_questions_after_answer = Column(Text)
    more_like_this = Column(Text)
    model = Column(Text)
    user_input_form = Column(Text)
    pre_prompt = Column(Text)
    agent_mode = Column(Text)
    speech_to_text = Column(Text)
    sensitive_word_avoidance = Column(Text)
    retriever_resource = Column(Text)

    dataset_query_variable = Column(String(255))
    prompt_type = Column(String(255), nullable=False, server_default="simple")

    chat_prompt_config = Column(Text)
    completion_prompt_config = Column(Text)
    dataset_configs = Column(Text)
    external_data_tools = Column(Text)
    file_upload = Column(Text)
    text_to_speech = Column(Text)

    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    def __repr__(self):
        return f"<AppModelConfig(id={self.id}, app_id={self.app_id}, provider={self.provider}, model_id={self.model_id})>"


class Position(BaseModel):
    x: float
    y: float


class NodeData(BaseModel):
    class Type(str, Enum):
        SOURCE = 'datasource'
        CHUNKER = 'knowledge-index'
        TOOL = 'tool'

    type: Type | str  # not limit to built-in types
    title: str | None = None
    selected: bool

    # datasource
    datasource_parameters: dict[str, Any] | None = None
    datasource_configurations: dict[str, Any] | None = None
    plugin_id: str | None = None
    provider_type: str | None = None
    provider_name: str | None = None
    datasource_name: str | None = None
    datasource_label: str | None = None
    plugin_unique_identifier: str | None = None

    # tool
    tool_parameters: dict[str, Any] | None = None
    tool_configurations: dict[str, Any] | None = None
    tool_node_version: str | None = None
    provider_id: str | None = None
    provider_icon: str | None = None
    tool_name: str | None = None
    tool_label: str | None = None
    tool_description: str | None = None
    is_team_authorization: bool | None = None
    paramSchemas: list[Any] | None = None
    params: dict[str, Any] | None = None

    # knowledge index
    index_chunk_variable_selector: list[str] | None = None
    keyword_number: int | None = None
    retrieval_model: dict[str, Any] | None = None
    chunk_structure: str | None = None
    indexing_technique: str | None = None
    embedding_model: str | None = None
    embedding_model_provider: str | None = None


class Node(BaseModel):
    @property
    def datasource_type(self): return self.data.provider_type
    id: str
    type: Literal['custom']
    data: NodeData
    position: Position
    targetPosition: str | None = None
    sourcePosition: str | None = None
    positionAbsolute: Position | None = None
    width: float | None = None
    height: float | None = None
    selected: bool


class Edge(BaseModel):
    id: str
    type: str
    source: str
    target: str
    sourceHandle: str | None = None
    targetHandle: str | None = None
    data: dict[str, Any] | None = None
    zIndex: int | None = None


class Viewport(BaseModel):
    x: float
    y: float
    zoom: float


class Graph(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    viewport: Viewport

    @property
    def datasources(self):
        return [node for node in self.nodes if node.data.type == NodeData.Type.SOURCE]

    @staticmethod
    def convert(*records: list[dict]):
        return [{**record, "graph": Graph(**json.loads(record["graph"]))} for record in records]
