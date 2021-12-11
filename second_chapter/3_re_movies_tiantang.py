import requests
import re
import csv

url = "https://dytt89.com/"
resp = requests.get(url) # verify=False  去掉安全验证
resp.encoding = "gb2312" # 指定编码
# print(resp.text)

# 提取必看电影 url 列表
re_comp1 = re.compile(r"2021必看热片.*?<ul>(?P<list_str>.*?)</ul>", re.S)
re_comp2 = re.compile(r"<li><a href='(?P<href>.*?)'.*?</li>")

href_list = []
iter1 = re_comp1.finditer(resp.text)
for it in iter1:
    list_str = it.group("list_str")
    iter2 = re_comp2.finditer(list_str)
    for itt in iter2:
        href = url + itt.group("href").strip("/")
        href_list.append(href)

# 提取子页面内容
re_comp3 = re.compile(r'◎片　　名　(?P<movie_title>.*?)<br />.*?<div id="downlist".*?<a href="(?P<download>.*?)"', re.S)
for href in href_list:
    resp_child = requests.get(href)
    resp_child.encoding = "gb2312"
    child_result = re_comp3.search(resp_child.text)
    # 电影名、下载链接
    print(child_result.group("movie_title"))
    print(child_result.group("download"))
