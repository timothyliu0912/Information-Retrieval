
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers
import threading
import re
import time
import json
import multiprocessing
from multiprocessing import Pool
import asyncio
import hashlib
import aiohttp
import sys

es = Elasticsearch(['localhost:9200'])
sem = asyncio.Semaphore(50)
upload = []
htmls = []
art_url = []
#resp_url = []
upload_data = []
def get_article(start):
    search_data = {
        "from":start,"size":1000
        }
    result = es.search(index='pool', body=search_data)
    return result

async def get_html(url):
    with(await sem):
        payload ={
            'from' : url,
            'yes' : 'yes'
            }
        async with aiohttp.ClientSession() as session:  # 获取session
            async with session.post( "https://www.ptt.cc/ask/over18", data = payload) as resp:
                async with session.get(url) as resp:  # 提出请求
                    html = await resp.text() # 直接获取到bytes
                    #resp_url.append(resp.url)
                    htmls.append(html)


def main_get_html(art_url):
    loop = asyncio.get_event_loop()           # 获取事件循环
    tasks = [get_html(url) for url in art_url]  # 把所有任务放到一个列表中
    loop.run_until_complete(asyncio.wait(tasks)) # 激活协程
def mon_to_num(mon):
    nums={
        'Jan':'1',
        'Feb':'2',
        'Mar':'3',
        'Apr':'4',
        'May':'5',
        'Jun':'6',
        'Jul':'7',
        'Aug':'8',
        'Sep':'9',
        'Oct':'10',
        'Nov':'11',
        'Dec':'12',
    }
    return nums.get(mon,None)


def multi_parse_html(html,url):
    url = str(url)
    md5 = hashlib.md5()
    md5.update(url.encode("utf-8"))
    hash_md5 = md5.hexdigest()
    art_soup = BeautifulSoup(html,"html.parser")
    art_inf =  art_soup.select("span.article-meta-value")
    info = [s.extract() for s in art_soup(['script','span'])]
    art_main = art_soup.select("div#main-content.bbs-screen.bbs-content")
    try:
        for i in art_main:
            art_main = i
        if art_inf:
            date = art_inf[3].text
            spilt_date = date.split()
            mon= mon_to_num(spilt_date[1])
            day = spilt_date[4]+'-'+ mon +'-'+spilt_date[2]
            final_date = day+' '+spilt_date[3]
            title = art_inf[2].text
            topic = art_inf[1].text
            author = art_inf[0].text
        else:
            title = " "
            topic = " "
            author = " "
            final_date = " "
        data = {
            "_index": "article",
            "_type": "art",
            "_id":hash_md5,
            "_source": {    
                'title': title,
                'topic': topic,
                'author': author,
                'url': url,
                'time': final_date,
                'content': art_main.text
            }
        }
        return data
    except:
        print("Unexpected error:", sys.exc_info()[0])

def main_parse_html(htmls,art_url):
    p = Pool(4)
    i = 0
    for html,url in zip(htmls,art_url):
        data = p.apply_async(multi_parse_html,args=(html,url))
        upload_data.append(data)
    p.close()
    p.join()

def insert_to_db(l):
    for r in upload_data:
        if r.get():
            l.append(r.get())
    a = helpers.bulk(es, l)


if __name__ == '__main__':
    start = 200000
    start_time = time.time()
    for i in range(100):
        res = get_article(start)
        #print(len(res["hits"]["hits"]))
        start += 1000
        art_url = []
        for i in res["hits"]["hits"]:
            art_url.append(i["_source"]["url"])
        main_get_html(art_url)
        main_parse_html(htmls,art_url)

        insert_to_db(upload)
        print(len(upload))
        upload.clear()
        htmls.clear()
        art_url.clear()
        upload_data.clear()
        
    end_time = time.time()
    total_time = end_time - start_time
    print(total_time)
