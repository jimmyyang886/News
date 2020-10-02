from sqlalchemy import create_engine
import requests
import pymysql
import random

engine = create_engine("mysql+pymysql://teb101Club:teb101Club@192.168.112.128/twstock??charset=utf8mb4", max_overflow=5)

def proxy_request_cycling(url, publisher, use_proxy):
    #engine = create_engine("mysql+pymysql://teb101Club:teb101Club@192.168.112.128/twstock??charset=utf8mb4", max_overflow=5)
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    headers={'user-agent' : useragent}
    proxies=proxy_arg(publisher)
    while True:
        try:
            if use_proxy==True:
                proxy = next(proxies)
                print('try:', proxy, url)
                ip = proxy.get('http').replace('http://', '').split(':')[0]
                port = proxy.get('http').replace('http://', '').split(':')[1]
                # print(ip, port)
                res=requests.get(url=url, headers=headers, verify=False, timeout=5, proxies=proxy)
                #res=requests.get(url=url, headers=headers, verify=False, proxies=proxy)
                #res = requests.get(url=url, headers=headers, proxies=proxy)
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
                   # query = "update freeproxy SET {} ='no' WHERE ip='{}' and port={};" \
                   #     .format(publisher, ip, port)
                    # print("update {}:{} state to no for {} ".format(ip, port, publisher))
                    #engine.execute(query)
            else:
                res=requests.get(url=url, headers=headers, verify=False, timeout=5)
                # res = requests.get(url=url, headers=headers, verify=False)
                time.sleep(random.uniform(3,7))
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
            #print(e)
            print('proxy_request_cycling error:', url)
            if use_proxy==True:
                query = "update freeproxy SET {} ='no' WHERE ip='{}' and port={};"\
                    .format(publisher, ip, port)
                print("update {}:{} state to no for {} ".format(ip, port, publisher))
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