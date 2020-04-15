import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import threading
import re
import time
url_list = ["https://www.ptt.cc/bbs/Gossiping/index.html","https://www.ptt.cc/bbs/Stock/index.html","https://www.ptt.cc/bbs/C_Chat/index.html"]

es = Elasticsearch(['localhost:9200'])

def insert_to_pool_url(url):
    search_data = {
        "query":{
            "term":{
                "url":url,
            }
        }
    }
    insert_data = {
        'url': url,
    }
    result = es.search(index='url_pool', body=search_data)
    if(result['hits']['total'] == 0):
        result = es.index(index='url_pool', doc_type='url', body=insert_data, id=None)
        return 1
    else:
        return 0
def art_pool(title,topic,author,url, time, content):
    search_data = {
        "query":{
            "term":{
                "url":url,
            }
        }
    }
    data = {
        'title': title,
        'topic': topic,
        'author': author,
        'url': url,
        'time': time,
        'content': content
        }
    result = es.search(index='article', body=search_data)
    if(result['hits']['total'] == 0):
        
        return 1
    else:
        return 0

def parse(url_list1,num): 
    url = url_list1[num]
    payload ={
        'from' : url_list1[num],
        'yes' : 'yes'
    }
    rs = requests.session()
    res = rs.post("https://www.ptt.cc/ask/over18",verify = False, data = payload)
    for i in range(3000):
        res = rs.get(url)
        soup = BeautifulSoup(res.text,"html.parser")
        topic = soup.select("div.title a")
        date = soup.select("div.meta div.author")
        up_page = soup.select("div.btn-group.btn-group-paging a")
        url = "https://www.ptt.cc"+up_page[1]["href"]
        check = insert_to_pool_url(url)
        art_pushes = soup.select("span.hl.f2")
        if(check == 1):
            for s in topic:
                art_url = "https://www.ptt.cc"+s["href"]
                art_res = rs.get(art_url)
                art_soup = BeautifulSoup(art_res.text,"html.parser")
                art_inf = art_soup.select("span.article-meta-value")
                art_len = len(art_inf)
                art_text = art_soup.get_text()
                if (art_len == 4):
                    start_pos = re.search('\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}',art_text).span()
                    end_pos = re.search('※',art_text).span()
                    if(start_pos[1] !=0) & (end_pos[0] != 0):
                        content = art_text[start_pos[1]:end_pos[0]]
                        #print(art_inf[2].text, art_inf[1].text,art_inf[0].text,art_inf[3].text)
                        res = art_pool(art_inf[2].text,art_inf[1].text,art_inf[0].text,art_url,art_inf[3].text,content)
                        #print(res)
                else: 
                    continue
        else:
            continue
        

if __name__ == '__main__':
    start_time = time.time()
    t_list=[]
    t1 = threading.Thread(target=parse,args=(url_list,0))
    t_list.append(t1)
    t2 = threading.Thread(target=parse,args=(url_list,1))
    t_list.append(t2)
    t3 = threading.Thread(target=parse,args=(url_list,2))
    t_list.append(t3)
    for t in t_list:
        t.start()

    for t in t_list:
        t.join()

    end_time = time.time()
    total_time = end_time - start_time
    #result = es.search(index='article')
    #print(result)
    print("所有任务结束，总耗时为：{}".format(total_time))
