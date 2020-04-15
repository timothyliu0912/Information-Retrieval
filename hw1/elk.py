from elasticsearch import Elasticsearch
import sys
es = Elasticsearch(['localhost:9200'])
mapping_url = {
   'properties': {
       'url': {
           'type': "keyword",
       },
       'md5': {
           'type': "keyword",
       }
   }
}
mapping_art = {
   'properties': {
       'title': {'type': "text", },
        'topic': {'type': "text",},
        'author': {'type': "text",},
        'url': { 'type': "keyword",},
        "date": {
        "format": "yyyy-MM-dd HH:mm:ss",
        "type": "date"
      },
      'content': {'type': "text", }
   }
}
# 先删除之前的索引
es.indices.delete(index='article',ignore=[400,404])
#s.indices.delete(index='pool',ignore=[400,404])
#es.indices.delete(index='board',ignore=400)

#es.indices.create(index='board', ignore=400)
es.indices.create(index='article',ignore=400)
#es.indices.create(index='pool', ignore=400)
#result = es.indices.put_mapping(index='pool', doc_type='url', body=mapping_url)
#result = es.indices.put_mapping(index='board', doc_type='url', body=mapping_url)
result = es.indices.put_mapping(index='article', doc_type='art', body=mapping_art)