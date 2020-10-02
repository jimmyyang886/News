#!/usr/bin/env python
# coding: utf-8

# # Download news in time range

# In[6]:


import datetime
import requests
import os
from bs4 import BeautifulSoup as bs
from codes import codes
from proxies_cyc import *
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# strptime function
def time_t(time,t_type = "%Y-%m-%d"):
    return datetime.datetime.strptime(time,t_type)

# last news id
# def last_id(path):
#     last_id = os.listdir("C:/Users/user/Desktop/t")[-1].split(".")[0]
#     return last_id

def get_last_id(txtpath):
    last_id_list = os.listdir(txtpath)
    if len(last_id_list)!=0:
        last_id_list.sort(reverse = True)
        ld=last_id_list[0].split(".")[0]
    else:
        ld='201800000001'
    return ld

# Parameter 1 & 2  = keyword , tag
# time range ,  Parameter 3 & 4  = start_date , end_date
def today_mag(publisher,keyword,tag,start_date,end_date,txtpath):
    article_id='299900000001'
    last_id = get_last_id(txtpath) 
    page = 1
    url = f"https://www.businesstoday.com.tw/group_search/article?keywords={keyword}"
    page_url = url + f"&page={page}&order=new&field=title"
    try:
        res = proxy_request_cycling(page_url, publisher, True)
        #res = requests.get(page_url)
        soup = bs(res.text, 'html.parser')
    #    print(soup.select('span')[4].text)
    #     if soup.select('span')[4].text[0] == "找不到相關結果,不妨換個關鍵字吧:)":
    #         break

        pub_date = soup.select("p[class='searchitem__date']")
        pub_date_t = time_t(pub_date[0].text[3:])

        end_date_t = time_t(end_date)
        start_date_t = time_t(start_date)

        while pub_date_t >= end_date_t or pub_date_t >= start_date_t:  



            #for _pub_date in pub_date:
            for i in range(len(pub_date)):
                #pub_date_t = time_t(_pub_date.text[3:])
                pub_date_t = time_t(pub_date[i].text[3:])

                #check   " start_date =< pub_date =< end_date "
                if pub_date_t <= end_date_t and pub_date_t >= start_date_t:

                    tag = soup.select("div[class='searchitem__content']")[i].select("span")[0].text
                    article_url = soup.select("a[class='searchitem__title-link']")[i].attrs['href']
                    #checking tag

                    if tag == '財經時事':
                        #request Article
                        try:
                            article_res = proxy_request_cycling(article_url, publisher, True)
                            #article_res = requests.get(article_url)
                            article_soup = bs(article_res.text, 'html.parser')

                            article_title = article_soup.select("title")[0].text.replace("\u3000","").split(" -")[0]
                            article_id = article_soup.select("meta[property='dable:item_id']")[0].attrs["content"]

                            if int(article_id) <= int(last_id):
                                print('stop update!!')
                                break

                            article_publisher = "今周刊"
                            article_pub_date = article_soup.select("meta[property='article:published_time']")[0].attrs["content"][0:10]
                            article_writter = article_soup.select("meta[property='dable:author']")[0].attrs["content"]
                            article_content = article_soup.select("div[itemprop=articleBody]")[0]                            .text.replace("\n","").replace("\r","").replace("\xa0","").replace("\u3000","")
                            #article_id = article_soup.select("meta[property='dable:item_id']")[0].attrs["content"]
                            print(f"write to {txtpath}/{article_id}.txt")
                            #print(f"{article_title}\n{article_id} {article_publisher}\n{article_pub_date} {article_writter}\n\n{article_content}\n\n\n")
                            with open(f"{txtpath}/{article_id}.txt","w",encoding = "utf-8") as text: 
                                text.write(f"Datetime:{article_pub_date}\nSource:{article_publisher}\nAuthor:{article_writter}\ntitle:{article_title}\n========\n{article_content}")
                        except IndexError:
                            continue

            last_id = get_last_id(txtpath)
            if int(article_id) <= int(last_id):
                print('stop update!!')
                break                 


            page_url = url + f"&page={page}&order=new&field=title"    
            #res = requests.get(page_url)
            res = proxy_request_cycling(page_url, publisher, True)
            soup = bs(res.text, 'html.parser')
            pub_date = soup.select("p[class='searchitem__date']")
            pub_date_t = time_t(pub_date[0].text[3:])
            page += 1
            
    except IndexError:
        print('{} is not exist'.format(page_url))
        pass


        
publisher= 'businesstoday'
tag = '財經時事'
start_date = '2018-01-01'
end_date = '2020-08-10'

for sid, v in codes.items():
    if v.type == "股票" and v.market == "上市":

        publisher = 'businesstoday'
        
        txtpath=publisher+'/'+sid+'_'+v.name
        
        #print(txtpath)

        if not os.path.exists(txtpath):
            os.makedirs(txtpath)
        else:
            last_id = get_last_id(txtpath)
            #print(last_id)
            
        today_mag(publisher, v.name,tag, start_date, end_date, txtpath)
        #today_mag(last_id, publisher, v.name, txtpath)


# In[ ]:


url= 'https://www.businesstoday.com.tw/group_search/article?keywords=東泥&page=1&order=new&field=title'
res = requests.get(url)

#print(res.text)

soup = bs(res.text, 'html.parser')

print(soup.select('span')[4].text)


# In[ ]:





# In[ ]:




