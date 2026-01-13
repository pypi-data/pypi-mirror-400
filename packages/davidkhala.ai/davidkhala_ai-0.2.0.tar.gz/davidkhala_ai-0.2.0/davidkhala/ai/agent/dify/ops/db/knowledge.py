from davidkhala.ai.agent.dify.ops.db import DB
from davidkhala.ai.agent.dify.ops.db.orm import Graph


class Dataset(DB):

    def dataset_queries(self, dataset_id, limit=20) -> list[str]:
        template = "select content from dataset_queries where source = 'app' and created_by_role = 'end_user' and dataset_id = :dataset_id limit :limit"
        return self.query(template, {'dataset_id': dataset_id, 'limit': limit}).scalars().all()

    @property
    def datasets(self):
        template = "select id, name, description, indexing_technique, index_struct, embedding_model, embedding_model_provider, collection_binding_id, retrieval_model, icon_info, runtime_mode, pipeline_id, chunk_structure from datasets"
        return self.get_dict(template)

    def is_pipeline(self, id: str):
        template = "select runtime_mode = 'rag_pipeline' from datasets where id = :id"
        return self.query(template, {'id': id}).scalar()

    @property
    def data_source_credentials(self):
        template = "select id, name, plugin_id, auth_type from datasource_providers"
        return self.get_dict(template)

    def credential_id_by(self, name, provider) -> list[str]:
        template = "select id from datasource_providers where name = :name and provider = :provider"
        return self.query(template, {'name': name, 'provider': provider}).scalars().all()

    def documents(self, dataset_id: str):
        template = "select id, name,created_from, created_at from documents where dataset_id = :dataset_id"
        return self.query(template, {'dataset_id': dataset_id})


class Document(DB):
    def hit_documents(self, top_k: int = 3):
        template = "SELECT dataset_id, document_id, content FROM document_segments ORDER BY hit_count DESC LIMIT :top_k"
        return self.get_dict(template, {'top_k': top_k})

    def id_by(self, name: str, dataset_id: str = None) -> list[str]:
        """multiple ids can be found"""
        template = "select id from documents where name = :name"
        if dataset_id:
            template = "select id from documents where name = :name and dataset_id = :dataset_id"
        return [str(uuid) for uuid in self.query(template, {'name': name, 'dataset_id': dataset_id}).scalars().all()]


class Pipeline(DB):
    @property
    def pipelines(self):
        """unique syntax for pgsql"""
        template = "SELECT DISTINCT ON (app_id) app_id, graph, rag_pipeline_variables FROM workflows where type = 'rag-pipeline' ORDER BY app_id, created_at DESC"
        return Graph.convert(*self.get_dict(template))

    def pipeline(self, app_id):
        template = "select id, graph, rag_pipeline_variables from workflows where type = 'rag-pipeline' and app_id = :app_id"
        dict_result = self.get_dict(template, {'app_id': app_id})
        assert len(dict_result) < 2
        return Graph.convert(*dict_result)
