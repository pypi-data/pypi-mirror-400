from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, TypedDict, Optional
from urllib.parse import urlparse

import requests

from davidkhala.ai.agent.dify.api import API, Iterator
from davidkhala.ai.agent.dify.model import Document as DocumentBase


class DatasetDict(TypedDict):
    id: str
    name: str
    description: str
    provider: str
    permission: str
    data_source_type: str
    indexing_technique: str
    doc_form: str
    runtime_mode: str
    is_published: bool
    enable_api: bool
    # stats
    app_count: int
    document_count: int
    word_count: int
    total_documents: int
    total_available_documents: int
    # embedding
    embedding_available: bool
    embedding_model: str
    embedding_model_provider: str
    retrieval_model_dict: dict
    external_retrieval_model: dict
    external_knowledge_info: dict


class Document(DocumentBase):
    data_source_info: dict[str, str]
    data_source_detail_dict: dict[str, dict]
    dataset_process_rule_id: str
    created_from: str
    created_by: str
    created_at: int
    tokens: int
    archived: bool
    display_status: str
    word_count: int
    hit_count: int
    doc_form: str
    doc_metadata: dict
    disabled_at: int
    disabled_by: str


class Dataset(API):
    def __init__(self, api_key: str, base_url="https://api.dify.ai/v1"):
        super().__init__(api_key, f"{base_url}/datasets")

    def paginate_datasets(self, page=1, size=20):
        r = self.request(self.base_url, "GET", params={
            'page': page,
            'limit': size,
        })
        return r

    def list_datasets(self) -> Iterable[list[DatasetDict]]:
        return Iterator(self.paginate_datasets, None)

    @property
    def ids(self):
        for sub_list in self.list_datasets():
            for dataset in sub_list:
                yield dataset['id']

    class Instance(API):
        def __init__(self, d: Dataset, dataset_id: str):
            super().__init__(d.api_key, f"{d.base_url}/{dataset_id}")

        def get(self):
            return self.request(self.base_url, "GET")

        def upload(self, filename, *, path=None, url=None, document_id=None):
            """
            don't work for .html
            work for .md
            """
            files = {}
            if path:
                with open(path, 'rb') as f:
                    content = f.read()
                if not filename:
                    filename = os.path.basename(path)
            elif url:
                r = requests.get(url)
                r.raise_for_status()
                if not filename:
                    parsed_url = urlparse(url)
                    filename = Path(parsed_url.path).name
                content = r.content
            files['file'] = (filename, content)
            if document_id:
                # don't work for html
                r = requests.post(f"{self.base_url}/documents/{document_id}/update-by-file", files=files,
                                  **self.options)
            else:
                r = requests.post(f"{self.base_url}/document/create-by-file", files=files, **self.options)
            r = self.on_response(r)
            return r['document']

        def paginate_documents(self, page=1, size=20):
            return self.request(f"{self.base_url}/documents", "GET", params={
                'page': page,
                'limit': size
            })

        def list_documents(self) -> Iterable[Document]:
            for document_batch in Iterator(self.paginate_documents, None):
                for document in document_batch:
                    yield Document(**document)

        def has_document(self, name) -> bool:
            return any(name == item['name'] for row in self.list_documents() for item in row)


class ChunkDict(TypedDict):
    id: str
    position: int
    document_id: str
    content: str
    sign_content: str  # trimmed version of content
    answer: Optional[str]  # only used in QA chunk
    word_count: int
    tokens: int
    keywords: Optional[list[str]]
    index_node_id: str  # chunk 在向量索引中的节点 ID
    index_node_hash: str  # hash of sign_content
    hit_count: int
    enabled: bool
    status: str  # 'completed'
    created_at: int  # timestamp
    updated_at: int  # timestamp
    completed_at: int  # timestamp
    created_by: str  # user id
    child_chunks: list
    error: Optional
    stopped_at: Optional[int]  # timestamp
    disabled_at: Optional[int]  # timestamp


class Document(API):
    def __init__(self, d: Dataset.Instance, document_id: str):
        super().__init__(d.api_key, f"{d.base_url}/documents/{document_id}")

    def exist(self):
        try:
            self.get()
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise e

    def get(self):
        return self.request(self.base_url, "GET")

    def paginate_chunks(self, page=1, size=20):
        return self.request(f"{self.base_url}/segments", "GET", params={
            'page': page,
            'limit': size
        })

    def list_chunks(self) -> Iterable[ChunkDict]:
        for chunk_batch in Iterator(self.paginate_chunks, None):
            for chunk in chunk_batch:
                yield chunk

    def delete(self):
        if self.exist():
            self.request(self.base_url, "DELETE")
class Chunk(API):
    def __init__(self, d: Document, segment_id: str):
        super().__init__(d.api_key, f"{d.base_url}/segments/{segment_id}")
    def get(self):
        r=  self.request(self.base_url, "GET")
        assert r['doc_form'] # optional value text_model
        return r['data']