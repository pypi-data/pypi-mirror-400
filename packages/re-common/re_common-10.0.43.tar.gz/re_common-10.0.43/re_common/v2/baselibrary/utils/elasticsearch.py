# elasticsearch[async]~=8.11.1
from typing import Any, Dict, List
from elasticsearch import AsyncElasticsearch, helpers

DEFAULT_CONFIG = {
    "hosts": [
        "http://192.168.32.97:9200",
        "http://192.168.32.99:9200",
        "http://192.168.32.101:9200",
        "http://192.168.32.103:9200",
    ],
    "basic_auth": ("elastic", "Zl2bWsOuvqi0IUwpvGhK"),
    "timeout": 60,
}


def get_es(config=DEFAULT_CONFIG):
    es = AsyncElasticsearch(**config)
    return es


async def update(es: AsyncElasticsearch, index: str, doc_id: str, doc: Dict[str, Any], doc_as_upsert: bool = False):
    return await es.update(index=index, id=doc_id, doc=doc, doc_as_upsert=doc_as_upsert)


async def bulk_update(es: AsyncElasticsearch, index: str, docs: List[Dict[str, Any]], doc_as_upsert: bool = False):
    """
    批量更新ES文档

    docs 格式示例：
    [
        {"_id": "1", "doc": {"field1": "value1"}},
        {"_id": "2", "doc": {"field2": "value2"}},
    ]
    """
    actions = []
    for item in docs:
        action = {
            "_op_type": "update",
            "_index": index,
            "_id": item["_id"],
            "doc": item["doc"],
            "doc_as_upsert": doc_as_upsert,
        }
        actions.append(action)
    return await helpers.async_bulk(es, actions=actions)
