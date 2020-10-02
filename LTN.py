#!/usr/bin/env python
# coding: utf-8

import datetime

from datetime import date

import os
import random
import time

import requests
from bs4 import BeautifulSoup as bs4
#from pathvalidate import sanitize_filename

from codes import codes
from proxies_cyc import *
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

headers = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/83.0.4103.97 Safari/537.36"}
domain = "https://news.ltn.com.tw/"
query = "search?keyword={keyword}&conditions={condition}&start_time={ST}&end_time={ET}&page={page}"




class ltn(object):
    def __init__(self, query_list, publisher, txtpath):
        self.query_list=query_list
        self.txtpath=txtpath
        self.publisher=publisher
        self.LastnID= self.dlcheck()
        self.news_id = 9999999

    def dlcheck(self):
        if len(os.listdir(self.txtpath)) != 0:
            nID = []
            for _file in os.listdir(self.txtpath):
                _nID = _file[:-4]
                nID.append(int(_nID))
                LastnID = max(set(nID))
        else:
            LastnID  = 888888
        return LastnID

    def start_query(self):

        url = domain + query.format(keyword=self.query_list["keyword"],
                                    condition=self.query_list["condition"],
                                    ST=self.query_list["start_time"],
                                    ET=self.query_list["end_time"],
                                    page=self.query_list["page"])
        print(f"URL: {url}\n")
        
        try:
            
            res = proxy_request_cycling(url, publisher, True)
            #web_session = requests.session()
            #res = web_session.get(url, headers=headers)
            soup = bs4(res.text, "html.parser")
            self.get_news_list(soup)
            
        except Exception as e:
            print("\n------ERROR----->")
            print(f"Catch an Exception: {e}\nURL:{url}")
            print("<------ERROR-----\n")
        pass
    
    def get_news_list(self,soup):
        news_class = ['business', 'weeklybiz', 'politics']
        news_list = soup.select("ul[class='searchlist boxTitle'] > li")
        for news in news_list:
            print(self.news_id, self.LastnID)
            if int(self.news_id) <= self.LastnID:
                break
            pub_time = news.select("span")[0].text
            article = news.select("a")[0]
            print(f"News: {article.text}\n"
                  f"Link: {article.attrs['href']}\n"
                  f"Class: {article.attrs['href'].split('/')[-3]}")
            if article.attrs['href'].split("/")[-3] in news_class:
                self.news_id = article.attrs['href'].split("/")[-1]

                if int(self.news_id)<=self.LastnID:
                    break
                
                if not self.isNewsExists(pub_time):
                    title = article.text
                    link = article.attrs['href']
                    self.get_each_news(pub_time, title, link)
                    # time.sleep(random.randint(2, 5))

        if int(self.news_id)>self.LastnID:
            self.next_page_if_exists(soup)
        pass

    def get_each_news(self, pub_time: str, title: str, link: str):
        
        try:
            res= proxy_request_cycling(link, publisher, True)
#             web_ss = requests.session()
#             res = web_ss.get(link, headers=headers)
            soup = bs4(res.text, "html.parser")
            self.get_each_news_content(pub_time, title, link, soup)
        except Exception as e:
            print(f"Catch an Exception: \nID: {self.news_id}\nMSG: {e}\n\n")
        pass
    

    def isNewsExists(self, pub_time):
        year = pub_time.split("-")[0]
        file_path = f"./News/{year}/{self.news_id}.txt"
        try:
            return os.path.exists(file_path)
        except Exception as e:
            print(f"Check News is Exists: {e}")
            return False

    def next_page_if_exists(self, soup):
        p_next = soup.select("a[data-desc='下一頁']")
        if len(p_next) > 0:
            self.query_list["page"] = p_next[0].attrs["href"].split("=")[-1]
            self.start_query()
        else:
            query_list["end_time"] = query_list["start_time"]
            query_list["start_time"] = query_list["start_time"] - datetime.timedelta(days=30 * 3)
            query_list["page"] = 1
            if query_list["start_time"] < datetime.datetime(2016, 1, 1).date():
                print(f"Search start time: {query_list['start_time']}")
                print(f"\n-----Finished-----\n\n")
                return
            else:
                self.start_query()

    def get_each_news_content(self, pub_time: str, title: str, link: str, soup: bs4):
        all_content = ''
        content_list = soup.findAll("p", attrs={'class': None})
        for content in content_list:
            # print(f"{content.text}")
            if '一手掌握經濟脈動' in content.text:
                break
            elif '示意圖' in content.text or len(content.text) <= 1:
                continue
            else:
                all_content += content.text
        # print(f"{all_content}")
        self.write_to_file( pub_time, title, link, all_content)
        pass

    def write_to_file(self, pub_time: str, title: str, link: str, content: str):
        current_year = pub_time.split("-")[0]
        try:
            os.makedirs(self.txtpath, exist_ok=True)
            #file_name = sanitize_filename(file_name)
        except IOError as e:
            print(f"Write Into File Error:\nTitle: {title}\nMSG: {e}")
        finally:
            print(f"\nWrite Into: {self.txtpath +'/'+ self.news_id + '.txt'}\n")
            #if len(file_name) > 0:
            with open(self.txtpath +'/'+ self.news_id + ".txt", "w+", encoding='utf-8') as f:
                f.write(f"")
                f.write(f"標題: {title}\n")
                f.write(f"時間: {pub_time}\n")
                # f.write(f"記者: {reporter}\n")
                f.write("========\n")
                f.write(content)
                f.close()
        pass


# Last Disconnect2019-09-22 ~ 2019-12-21
# Stop at 2019-03-26 ~ 2019-06-24
# Stop at 2018-03-31 ~ 2018-06-29
# Stop at 2017-01-05 ~ 2017-04-05
#now = datetime.datetime(2017, 4, 5).date()


now = date.today()
start_time = time.time()



for sid, v in codes.items():
    
    if v.type == "股票" and v.market == "上市":

        publisher = 'LTN'
        
        txtpath=publisher+'/'+sid+'_'+v.name

        if not os.path.exists(txtpath):
            os.mkdir(txtpath)

        query_list = {"keyword": v.name, "condition": "and", "start_time": now - datetime.timedelta(days=30 * 3),
                      "end_time": now, "page": 1}

        stock=ltn(query_list, publisher, txtpath)
        stock.start_query()




