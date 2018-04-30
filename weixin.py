# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import json
import requests
import io
import re
import random

user="fcscucs@sina.com"
password="fcbayern07"
#设置要爬取的公众号列表
gzlist=['新世相']

def weChat_login():
    post = {}
    print("启动浏览器，打开微信公众号登录界面")
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
    driver.get('https://mp.weixin.qq.com/')
    time.sleep(5)
    print("正在输入微信公众号登录账号和密码...")
    sreach_window = driver.current_window_handle
    #driver.find_element_by_xpath("./*//input[@id='account']").clear()
    #driver.find_element_by_xpath("./*//input[@id='account']").send_keys(user)
    driver.find_element_by_xpath("//*[@id='header']/div[2]/div/div/form/div[1]/div[1]/div/span/input").send_keys(user)
    #driver.find_element_by_xpath("./*//input[@id='pwd']").clear()
    #driver.find_element_by_xpath("./*//input[@id='pwd']").send_keys(password)
    driver.find_element_by_xpath("//*[@id='header']/div[2]/div/div/form/div[1]/div[2]/div/span/input").send_keys(password)
    print("请在登录界面点击:记住账号")
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='header']/div[2]/div/div/form/div[4]/a").click()
    print("请拿手机扫码二维码登录公众号")
    time.sleep(5)
    print("登录成功")
    driver.get('https://mp.weixin.qq.com/')
    cookie_items = driver.get_cookies()

    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post, ensure_ascii=False)
    if isinstance(cookie_str, str):
        cookie_str = cookie_str.decode("utf-8")
    with io.open('cookie.txt', 'w+', encoding='utf-8') as f:
        f.write(cookie_str)
    print("cookies信息已保存到本地")

def get_content(query):
    url = 'https://mp.weixin.qq.com'
    header = {
        "HOST": "mp.weixin.qq.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    with io.open('cookie.txt', 'r', encoding ='utf-8') as f:
        cookie = f.read()
    cookies = json.loads(cookie)
    response = requests.get(url=url, cookies=cookies)
    token = re.findall(r'token=(\d+)', str(response.url))

    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    query_id = {
        'action': 'search_biz',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5'
    }

    search_response = requests.get(search_url, cookies=cookies, headers=header, params=query_id)
    lists = search_response.json().get('list')[0]
    fakeid = lists.get('fakeid')
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    query_id_data = {
        'token': token ,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '0',  # 不同页，此参数变化，变化规则为每页加5
        'count': '5',
        'query': '',
        'fakeid': fakeid,
        'type': '9'
    }

    #print("OJBK3")

    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
    max_num = appmsg_response.json().get('app_msg_cnt')
    num = int(int(max_num) / 5)
    begin = 0
    while num + 1 > 0:
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '{}'.format(str(begin)),
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
        }
        print('正在翻页：--------------', begin)

    query_fakeid_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
    fakeid_list = query_fakeid_response.json().get('app_msg_list')
    for item in fakeid_list:
        content_link = item.get('link')
        content_title = item.get('title')
        fileName = query + '.txt'
        with io.open(fileName, 'a', encoding='utf-8') as fh:
            fh.write(content_title + ":\n" + content_link + "\n")
    num -= 1
    begin = int(begin)
    begin += 5
    time.sleep(2)

if __name__=='__main__':
    #try:
        weChat_login()
        for query in gzlist:
            print("开始爬取公众号："+query)
            get_content(query)
            print("爬取完成")
    #except Exception as e:
    #    print(str(e))


