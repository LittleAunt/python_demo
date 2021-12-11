import requests
from bs4 import BeautifulSoup

url = "https://www.dytt8.net/index2.htm"

resp = requests.get(url)
resp.encoding = "gb2312"

page = BeautifulSoup(resp.text, "html.parser")

# find 找一个，find_all 找所有
# find("div", class_="co_content2") ，class 是 python 关键字，因此加下划线做区分，或用 attrs
movie_list = page.find("div", attrs={
    "class": "co_content2"
})
movie_names = movie_list.find_all("a")
for name in movie_names:
    print(name.text)

