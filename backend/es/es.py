import os

from elasticsearch_async import AsyncElasticsearch

from config import config
from es.mapping import INDEX

client = {}
INDEX_NAME = 'openpacs'


async def setup():
    global client
    conn = AsyncElasticsearch(hosts=[config['es_host']])
    client[os.getpid()] = conn
    try:
        await get_client().indices.get(index=INDEX_NAME)
    except Exception as e:
        if getattr(e, 'error', '') == 'index_not_found_exception':
            await get_client().indices.create(index=INDEX_NAME, body=INDEX)
        else:
            raise


async def teardown():
    await close()
    del client[os.getpid()]


async def close():
    await get_client().transport.close()


def get_client():
    return client[os.getpid()]


async def index(data):
    await get_client().index(index=INDEX_NAME, id=data['id'], body=data)


async def delete(id_):
    await get_client().delete(index=INDEX_NAME, id=id_)


columns = [
    "Patient's Name", 'SOP Class UID', 'Study Description', 'Series Description',
    "Referring Physician's Name", "Performing Physician's Name",
]


async def search(data):
    size = data.pop('results', 10)
    page = data.pop('page', 1)

    query = data.get('query', '').lower()
    if query != '':
        es_q = {
            "multi_match": {
                "query": query,
                "fields": [
                    "Patient ID",
                    "Patient's Name.lang_analyzed",
                    "SOP Class UID.lang_analyzed",
                    "Study Description.lang_analyzed",
                    "Series Modality",
                    "Series Description.lang_analyzed",
                    "Referring Physician's Name.lang_analyzed",
                    "Performing Physician's Name.lang_analyzed",
                ],
                "operator": "and",
            }
        }
    elif len(data) > 0:
        es_q = []

        for k, v in data.items():
            if not v: continue

            if k in columns:
                k += ".lang_analyzed"
            es_q.append({"match": {k: v[0]}})

        es_q = {"bool": {"must": es_q}}
    else:
        es_q = {"match_all": {}}

    res = await get_client().search(
        index=INDEX_NAME,
        body={
            "query": es_q,
            "size": size,
            "from": (page - 1) * size,
        })
    return {
        'data': [r['_source'] for r in res['hits']['hits']],
        'total': res['hits']['total']['value'],
    }


async def index_file(file):
    data = {
        'id': file['id'],
        'patient_db_id': file['patient_db_id'],
        'study_db_id': file['study_db_id'],
        'series_db_id': file['series_db_id'],
    }
    data.update(file['meta'])
    await index(data)


async def reset_index():
    await get_client().indices.delete(index='openpacs')
    await get_client().indices.create(index='openpacs', body=INDEX)

