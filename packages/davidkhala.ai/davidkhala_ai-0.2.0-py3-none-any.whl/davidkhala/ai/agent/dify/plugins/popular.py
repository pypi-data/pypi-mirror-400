model_provider = [
    'langgenius/siliconflow',
    'langgenius/azure_openai',
    'langgenius/tongyi',
    'langgenius/jina',
    'langgenius/openrouter',
    'langgenius/deepseek',
]

class Knowledge:
    data_source = [
        'langgenius/firecrawl_datasource',
    ]
    chunk = [
        'langgenius/parentchild_chunker',
        'langgenius/general_chunker',
    ]
    api = [
        'abesticode/knowledge_pro',
    ]

class Node:
    format = [
        'langgenius/json_process',
        'langgenius/dify_extractor',
    ]
    agent = [
        'langgenius/agent',
    ]
    data = [
        'langgenius/chart',
        'junjiem/db_query',
        'junjiem/db_query_pre_auth',
    ]


