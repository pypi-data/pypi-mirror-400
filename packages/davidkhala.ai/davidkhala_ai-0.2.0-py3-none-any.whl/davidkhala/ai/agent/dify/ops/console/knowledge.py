from time import sleep

from davidkhala.utils.http_request.stream import as_sse, Request as StreamRequest
from pydantic import BaseModel

from davidkhala.ai.agent.dify.interface import IndexingError
from davidkhala.ai.agent.dify.model import Document, Dataset
from davidkhala.ai.agent.dify.const import IndexingStatus
from davidkhala.ai.agent.dify.ops.console import API
from davidkhala.ai.agent.dify.ops.console.session import ConsoleUser
from davidkhala.ai.agent.dify.ops.db.orm import Node


class ConsoleKnowledge(API):
    def __init__(self, context: ConsoleUser):
        super().__init__()
        self.base_url = context.base_url
        self.session.cookies = context.session.cookies
        self.options = context.options


class Datasource(ConsoleKnowledge):
    """step 1: Choose a Data Source"""

    class FirecrawlOutput(BaseModel):
        source_url: str
        description: str
        title: str
        credential_id: str
        content: str

    def run_firecrawl(self, pipeline: str, node: Node,
                      *,
                      inputs: dict,
                      credential_id: str
                      ):

        url = f"{self.base_url}/rag/pipelines/{pipeline}/workflows/published/datasource/nodes/{node.id}/run"

        stream_request = StreamRequest(self)
        response = stream_request.request(url, 'POST', json={
            'inputs': inputs,
            'datasource_type': node.datasource_type,
            'credential_id': credential_id,
            "response_mode": "streaming"
        })

        for data in as_sse(response):
            event = data['event']
            if event == 'datasource_completed':
                return data['data']
            else:
                assert event == 'datasource_processing'
                print(data)
        return None

    def upload(self):
        "http://localhost/console/api/files/upload?source=datasets"
        # TODO
        "form data"
        {
            "file": "body"
        }
        r = {
            "id": "3898db5b-eb72-4f11-b507-628ad5d28887",
            "name": "Professional Diploma Meister Power Electrical Engineering - Technological and Higher Education Institute of Hong Kong.html",
            "size": 254362,
            "extension": "html",
            "mime_type": "text\/html",
            "created_by": "dbd0b38b-5ef1-4123-8c3f-0c82eb1feacd",
            "created_at": 1764943811,
            "source_url": "\/files\/3898db5b-eb72-4f11-b507-628ad5d28887\/file-preview?timestamp=1764943811&nonce=43b0ff5a13372415be79de4cc7ef398c&sign=7OJ2wiVYc4tygl7yvM1sPn7s0WXDlhHxgX76bsGTD94%3D"
        }


class Operation(ConsoleKnowledge):
    def website_sync(self, dataset: str, document: str, *, wait_until=True):
        """
        cannot be used towards a pipeline dataset. Otherwise, you will see error "no website import info found"
        """
        doc_url = f"{self.base_url}/datasets/{dataset}/documents/{document}"

        r = self.request(f"{doc_url}/website-sync", "GET")
        assert r == {"result": "success"}
        if wait_until:
            return self.wait_until(dataset, document)
        return None

    def retry(self, dataset: str, *documents: str, wait_until=True):
        """
        It cannot trigger rerun on success documents
        """
        url = f"{self.base_url}/datasets/{dataset}/retry"
        self.request(url, "POST", json={
            'document_ids': documents,
        })
        # response status code will be 204
        if wait_until:
            return [self.wait_until(dataset, document) for document in documents]
        return None

    def rerun(self, dataset: str, *documents: str):
        for document in documents:
            try:
                self.website_sync(dataset, document)
                assert False, "expect IndexingError"
            except IndexingError:
                pass
        return self.retry(dataset, *documents)

    def wait_until(self, dataset: str, document: str, *,
                   expect_status=None,
                   from_status=None,
                   interval=1
                   ):
        if not expect_status:
            expect_status = [IndexingStatus.FAILED, IndexingStatus.COMPLETED]
        url = f"{self.base_url}/datasets/{dataset}/documents/{document}/indexing-status"
        if from_status is None:
            from_status = [IndexingStatus.WAITING, IndexingStatus.PARSING]
        r = self.request(url, "GET")
        status = r['indexing_status']
        assert status in from_status, f"current status: {status}, expect: {from_status}"
        while status not in expect_status:
            sleep(interval)
            r = self.request(url, "GET")
            status = r['indexing_status']
        if status == IndexingStatus.FAILED: raise IndexingError(r['error'])
        return r


class DatasetResult(Dataset):
    chunk_structure: str

class RunResult(BaseModel):
    batch: str
    dataset: DatasetResult
    documents: list[Document]

class Load(ConsoleKnowledge):
    """
    Processing Documents
    """

    def async_run(self, pipeline: str, node: Node, inputs: dict, datasource_info_list: list[dict])->RunResult:
        """Ingest new document"""
        url = f"{self.base_url}/rag/pipelines/{pipeline}/workflows/published/run"
        r = self.request(url, "POST", json={
            'inputs': inputs,
            'start_node_id': node.id,
            'is_preview': False,
            'response_mode': "blocking",
            "datasource_info_list": datasource_info_list,
            'datasource_type': node.datasource_type
        })
        return RunResult(**r)


