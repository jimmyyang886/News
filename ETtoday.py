#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, requests, time, re
from bs4 import BeautifulSoup

from datetime import date

import random
from codes import codes
from proxies_cyc import *
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from codes import codes

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.138 Safari/537.36'
}

def dlcheck(txtpath):
    if len(os.listdir(txtpath))!=0:
        nID=[]
        for _file in os.listdir(txtpath):
            _nID=_file[:-4]

            #if _nID.split('-')[1]=='260410':
            nID.append(int(_nID.split('_')[1]))
            LastnID = max(set(nID))
    else:
        LastnID = 1

    return LastnID



def crawler(publisher,sName, txtpath):
    newsid_no=9999999
    lastId=dlcheck(txtpath)
    #print('lastId:', lastId)
    page=1
    while newsid_no >= lastId:
        url = f'https://www.ettoday.net/news_search/doSearch.php?keywords={sName}&kind=17&page={page}'
        #resp = requests.get(url, headers=headers, timeout=10)
        res = proxy_request_cycling(url, publisher, True)
        soup = BeautifulSoup(res.text, 'lxml')

        try:
            page_t = soup.select('div.page_nav')[0].select('p.info')[0].text
            page_t = page_t.split('|')[1]
            max_page = re.findall('[0-9]{1,5}', page_t)[0]
            print('keyword:{}, current page:{} max_page:{}'.format(sName,page,max_page))
            #print(article_url_list)

            article_url_list = soup.select('h2')

            for article_url in article_url_list:
                #article_url.select('a')['href']
                #print(article_url)
                url = article_url.select('a')[0]['href']

                #res = requests.get(url, headers=headers, timeout=20)
                res = proxy_request_cycling(url, publisher, True)



                #print(res.text)
                soup = BeautifulSoup(res.text, 'lxml')
                try:

                    title = soup.find('article').find('header').text.replace('\u3000', ' ').strip()
                    content = soup.find('article').find('div', class_='story').find_all('p')
                    time = soup.find('time', class_='date').text.strip()

                    newsid = re.findall('[0-9]{1,}/[0-9]{1,}',url)[0].replace('/','_')

                    #print(newsid)
                    newsid_no = int(newsid.split('_')[1])
                    dateinfo=int(newsid.split('_')[0])

                    #print(dateinfo)
                    #print('currentID:', newsid_no)

                    if newsid_no<lastId:
                        break

                    if dateinfo < 20160101:
                        break

                    if len(content[1].text)>len(content[2].text):
                        author = content[2].text
                        content.remove(content[2])
                    else:
                        author = content[1].text
                        content.remove(content[1])

                    contents=''
                    for i in range(2,len(content)-1):
                        contents = contents + content[i].text

                    # if not os.path.exists('etoday'):
                    #     os.mkdir('ettoday')

                    print('write to :{}/{}.txt'.format(txtpath, newsid))

                    with open('{}/{}.txt'.format(txtpath, newsid),'w', encoding = 'utf-8') as w:
                        w.write('title: '+title + '\n\n')
                        w.write('author: '+author + '\n\n')
                        w.write('time: '+time + '\n\n')
                        w.write('=======\n\n')
                        w.write(contents)

                except Exception as e:
                    print(e)
                    pass
        except IndexError:
           pass

        page += 1
        if page > int(max_page):
            break

publisher='ettoday'

for code, v in codes.items():
    if v.type == "股票" and v.market == "上市":

        txtpath=publisher+'/'+code+'_'+v.name
        if not os.path.exists(txtpath):
            os.mkdir(txtpath)

        print('searching for updated news:', v.name)
        crawler(publisher, v.name, txtpath)