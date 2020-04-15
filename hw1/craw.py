import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers
import re
import time
import asyncio
import hashlib
md5 = hashlib.md5()
es = Elasticsearch(['localhost:9200'])

def insert_to_pool(url_topic):
    result  = 0
    insert = []
    
    for i in url_topic:
        md5 = hashlib.md5()
        md5.update(i.encode("utf-8"))
        hash_md5 = md5.hexdigest()
        insert_data = {
            "_index": "pool",
            "_type": "url",
            "_id":hash_md5,
            "_source": {
                    'url':i,
                }
            }
        insert.append(insert_data)
    a = helpers.bulk(es, insert)

async def parse(url,rs):
    url_board = "https://www.ptt.cc"+url["href"]
    board = []
    for i in range(500):
        res = await loop.run_in_executor(None,rs.get,url_board)
        soup = BeautifulSoup(res.text,"html.parser")
        up_page = soup.select("div.btn-group.btn-group-paging a")
        topic = soup.select("div.title a")

        url_topic = []
        for i in topic:
            url_topic.append("https://www.ptt.cc"+i["href"])

        insert_to_pool(url_topic)
        
        last_page = re.search('disabled', str(up_page[1]))
        #判斷最後一頁
        if last_page != None:
            break
        else:
            url_board = "https://www.ptt.cc"+up_page[1]["href"]
            md5 = hashlib.md5()
            md5.update(url_board.encode("utf-8"))
            hash_md5 = md5.hexdigest()
            search_data = {
                "query":{
                    "term":{
                        "_id":hash_md5,
                    }
                }
            }
            result = es.search(index='board', body=search_data)
            if(result['hits']['total'] == 0):
                insert_data = {
                    "_index": "board",
                    "_type": "url",
                    "_id":hash_md5,
                    "_source": {
                            'url':url_board,
                        }
                    }
                board.append(insert_data)
        a =helpers.bulk(es, board)
        
        


if __name__ == '__main__':
    
    url = 'https://www.ptt.cc/bbs/hotboards.html'
    payload ={
        'from' : url,
        'yes' : 'yes'
    }
    rs = requests.session()
    res = rs.post("https://www.ptt.cc/ask/over18",verify = False, data = payload)
    res = rs.get(url)
    soup = BeautifulSoup(res.text,"html.parser")
    boards = soup.select("div.b-ent a.board")
    #取得最上頁
    start_time = time.time()
    loop = asyncio.get_event_loop()
    tasks = [parse(url,rs) for url in boards]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    end_time = time.time()
    total_time = end_time - start_time
    print("所有任务结束，总耗时为：{}".format(total_time))
