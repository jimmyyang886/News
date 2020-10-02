#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import json
# from random import choice
# from proxy import get_proxy
from datetime import datetime, date
import requests, os  , time

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


from Anue_api.proxies_cyc import *
from Anue_api.anue_crawler import Anue


txtpath='Anue'
publisher='Anue'
start =  int(time.time()) + 2592000 + 86400 #target --> now + one month (one month limit)
old   = int(time.time()) + 86400

def get_last_id(txtpath):
    last_id_list = os.listdir(txtpath)
    last_id_list.sort(reverse = True)
    return int(last_id_list[0].split(".")[0])


def get_newsid(last_id, start,old, publisher, txtpath):
    #newsid = []
    
#     while (start > 1577808000):
#         # 抓到 2020/01/01 為止
    start = start- 2592000 - 86400 
    old = old - 2592000 - 86400 
#         print(date.fromtimestamp(start))
#         print(date.fromtimestamp(old))   
#        for i in range(1,20):
    i=1
    
    newsid=9999999
    
    while int(last_id) < newsid:
                
        url = 'https://news.cnyes.com/api/v3/news/category/tw_stock?startAt='        +str(old)+'&endAt='+str(start)+'&limit=30&page={}'.format(i)

        res=proxy_request_cycling(url, publisher,True)

        #res = requests.get(url)
        #time.sleep(random.uniform(3,7))
        try:
            jsonData = json.loads(res.text)
            #print(jsonData)
        except:
            continue

        try:
            if jsonData['items']['next_page_url'] == '/api/v3/news/category/tw_stock?page=2':
                continue
            else:
                soup =  jsonData['items']['data']
        except KeyError:
            continue

        for x in soup:
            try:

                newsid=x['newsId']                    
                news =  Anue(newsid, txtpath, publisher)
                news.run()     
                print(newsid, last_id)
               
                if len(x['summary']) ==0:
                    pass

                elif int(newsid) <= int(last_id):
                    break
                
                #newsid.append(x['newsId'])
            except TypeError:
                pass
        i+=1
        
        last_id=get_last_id(txtpath)

last_id=get_last_id(txtpath)
get_newsid(last_id, start, old, publisher, txtpath)

print("update complete!!")


# In[ ]:




