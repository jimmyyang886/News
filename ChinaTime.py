#!/usr/bin/env python
# coding: utf-8

import os
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import re
from datetime import datetime
import time

from sqlalchemy import create_engine
import pymysql

import random

engine = create_engine("mysql+pymysql://teb101Club:teb101Club@192.168.112.128/twstock??charset=utf8mb4", max_overflow=5)

class ChinaTime(object):
    
    def __init__(self, sName, txtpath):
        self.sName=sName
        self.txtpath=txtpath
        self.curDatetime=datetime.now()
        self.page=0
        self.LastnIDcheck()
        #self.curnIDcheck()
        self.curnID=20990806000413
    
    def LastnIDcheck(self):   
    
        if len(os.listdir(self.txtpath))!=0:
            nID=[]
            for _file in os.listdir(self.txtpath):
                _nID=_file[:-4]
                #if _nID.split('-')[1]=='260410':
                nID.append(_nID.split('-')[0])
            self.LastnID = max(set(nID))
        else:
            self.LastnID = '20180101000000'
        return self.LastnID
    
    # def curnIDcheck(self):
    #     tag = ['260202', '260206', '260210', '260410']
    #     useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    #     headers={'user-agent' : useragent}
    #     url='http://www.chinatimes.com/search/{}?page={}&chdtv'.format(self.sName, 1)
    #     res = proxy_request_cycling(url, 'chinatime', True)
    #     #res=requests.get(url=url, headers=headers, verify=False)
    #     soup= BeautifulSoup(res.text, 'html.parser')
    #
    #
    #     # article_url=soup.select('h3')[0].select('a')[0]['href']
    #     article_url_list = soup.select('h3')
    #
    #     for article_url in article_url_list:
    #         article_url=article_url.select('a')[0]['href']
    #         nID=re.findall('\d+.-\d+', article_url.split('?')[0])[0]
    #         if nID.split('-')[1] in tag:
    #             self.curnID=nID.split('-')[0]
    #             break
    #     return self.curnID
        
    def fetch(self):
        #page=1
        #while self.curDatetime > self.LastDatetime:
        tag = ['260202', '260206', '260210', '260410']
        while int(self.curnID) >= int(self.LastnID):

            self.page+=1

            url='http://www.chinatimes.com/search/{}?page={}&chdtv'.format(self.sName, self.page)
            
            #infinite loop for available proxies
            print('request to {}'.format(url))
            res = proxy_request_cycling(url, 'chinatime', True)
            #res = proxy_request_cycling(url, 'chinatime', False)
            soup = BeautifulSoup(res.text, 'html.parser')

            try:
                # for empty and wrong page searching
                if soup.select('span.search-result-count')[0].text == '00':
                    break
            except Exception as e:
                #print(e)
                pass

            try:
                articles=soup.select('h3')
                pstimes=soup.select('div.meta-info')
            except IndexError:
                break

            for _pstime, _article in zip(pstimes , articles):
                try:
                    article_time= _pstime.select('time')[0]['datetime']
                    self.curDatetime = datetime.strptime(article_time, "%Y-%m-%d %H:%M")

                    title=_article.select('a')[0].text
                    article_url=_article.select('a')[0]['href']

                    nID=re.findall('\d+.-\d+', article_url.split('?')[0])[0]
                    if nID.split('-')[1] in tag:
                        self.curnID=nID.split('-')[0]
                        if int(self.curnID) <= int(self.LastnID):
                            print('update is done :', self.sName, self.curnID )
                            break
                        else:
                            print('update progress...', self.sName, self.curnID)

                    else:
                        print('{} is not financial news.....'.format(article_url))
                        continue

                    # confirm article url
                    if re.findall('www.chinatimes.com', article_url) != []:
                        print('request to {} by {}'.format(article_url, self.sName))
                        res=proxy_request_cycling(article_url, 'chinatime', True)
                        #res = proxy_request_cycling(article_url, 'chinatime', False)
                    else:
                        print('wrong url:', article_url)
                        continue

                    if res.status_code !=200:
                        error = "error:{},page:{},title:{},url:{}".format(res.status_code, self.page
                                                                                      ,title, article_url)
                        with open('error.log', 'a+', encoding='utf-8') as f:
                            f.write(error)
                            f.write('\n')
                        continue

                except Exception as e:
                    #print(e)
                    print("article_url is error {} : {} ".format(self.page, title), article_url)
                    error="error:{}, article_url is error - page: {},title:{},url:{}".format(str(e), self.page
                                                                                             , title, article_url)
                    with open('error.log', 'a+', encoding='utf-8') as f:
                        f.write(error)
                        f.write('\n')
                    continue
                #print(res.text)

                try:
                    soup=BeautifulSoup(res.text, 'html.parser')
                    rtime=soup.select('time')[0]['datetime']
                    source=soup.select('div.source')[0].text
                    author=soup.select('div.author')[0].text.replace('\n','')
                    #print(rtime, source, author)
                    title=soup.select('meta')[4]['content'].split(' -')[0]
                    #content=soup.select('meta')[9]['content']
                    content = soup.select('div.article-body')[0].text

                    #txtcontent=''
                    txtcontent='Datetime: '+rtime+'\n'
                    txtcontent+='Source: '+source+'\n'
                    txtcontent+='Author: '+author+'\n'
                    txtcontent+='title: '+title+'\n'
                    txtcontent+='=============='+'\n'
                    txtcontent+=content

                    filename = nID + '.txt'
                    with open(self.txtpath+'/'+filename, 'w', encoding='utf-8') as f:
                        f.write(txtcontent)
                    print('page:{} to filename:{}'.format(self.page, filename))
                    #time.sleep(1)

                except Exception as e:
                    print(e)
                    print("article_url is error {} : {} ".format(self.page, title))
                    error="error:{}, url error - page: {},title:{},url:{}".format(str(e), self.page, title, article_url)
                    with open('error.log', 'a+', encoding='utf-8') as f:
                        f.write(error)
                        f.write('\n')
                    continue



def proxy_request_cycling(url, publisher, use_proxy):
    #engine = create_engine("mysql+pymysql://teb101Club:teb101Club@192.168.112.128/twstock??charset=utf8mb4", max_overflow=5)
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    headers={'user-agent' : useragent}
    proxies=proxy_arg(publisher)
    while True:
        try:
            if use_proxy==True:
                proxy = next(proxies)
                #print('try:', proxy, url)
                ip = proxy.get('http').replace('http://', '').split(':')[0]
                port = proxy.get('http').replace('http://', '').split(':')[1]
                # print(ip, port)
                res=requests.get(url=url, headers=headers, verify=False, timeout=5, proxies=proxy)
                #res = requests.get(url=url, headers=headers, proxies=proxy, verify=False)

                if res.status_code == 200:
                    query = "update freeproxy SET {} ='yes' WHERE ip='{}' and port={} and {}<>'yes' or {} is null;"\
                            .format(publisher, ip, port, publisher, publisher)
                    # print("update {}:{} state to yes for {} ".format(ip, port, publisher))
                    engine.execute(query)
                    # next(proxies)
                    break

                else:
                    if res.status_code == 404:
                        print(res.status_code, url)
                        break
                    continue

                # else:
                #     query = "update freeproxy SET {} ='no' WHERE ip='{}' and port={};" \
                #         .format(publisher, ip, port)
                #     # print("update {}:{} state to no for {} ".format(ip, port, publisher))
                #     engine.execute(query)
            else:
                res=requests.get(url=url, headers=headers, verify=False, timeout=5)
                # res = requests.get(url=url, headers=headers, verify=False)
                time.sleep(2)
                if res.status_code == 200:
                    break
                else:
                    if res.status_code == 404:
                        print(res.status_code, url)
                        break
                    continue

        except StopIteration:
            proxies=proxy_arg(publisher)
            continue

        except Exception as e:
            # print(e)
            print('proxy_request_cycling error:', url)
            if use_proxy==True:
                query = "update freeproxy SET {} ='no' WHERE ip='{}' and port={};"\
                    .format(publisher, ip, port)
                #print("update {}:{} state to no for {} ".format(ip, port, publisher))
                engine.execute(query)
                continue
    return res
        
            
def proxy_arg(publisher):
    query = "SELECT ip, port FROM freeproxy WHERE active = 'yes' and ({} is null or {} <>'no');"\
            .format(publisher, publisher)
    proxies_list=list(engine.execute(query))

    random.shuffle(proxies_list)
    #print(proxies_list)

    #temp solution - proxy pool is empty in DB for certain publisher.
    if len(proxies_list)<5:
        query = "update twstock.freeproxy  set {} = 'yes' where active='yes';"\
            .format(publisher)
        engine.execute(query)

        query = "update twstock.freeproxy  set {} = 'no' where active='no';" \
            .format(publisher)
        engine.execute(query)


    for _iport in proxies_list:

        http = 'http://'+_iport[0] +':' + str(_iport[1])
        https ='https://'+_iport[0] +':' + str(_iport[1])

        proxies = {
            'http': http,
            'https': https,
        }

        yield proxies

if __name__ == '__main__':

    from codes import codes

    for code, v in codes.items():
        if v.type == "股票" and v.market == "上市":
            #sName=v.name
            #print(sName)
            publisher='chinatime'

            '''      
            proxies=proxy_arg(publisher)
            while True:
                try: 
                    print(next(proxies))
                    time.sleep(2)

                except StopIteration:
                    proxies=proxy_arg()
            '''

            txtpath=publisher+'/'+code+'_'+v.name

            if not os.path.exists(txtpath):
                os.mkdir(txtpath)

            stock=ChinaTime(v.name, txtpath)

            print('searching for updated news:', v.name)
            # print('curnID:', stock.curnID)
            # print('LastnID:', stock.LastnID)

            stock.fetch()