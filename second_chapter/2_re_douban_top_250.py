import requests
import re
import csv

# 请求数据
url = "https://movie.douban.com/top250"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
}
resp = requests.get(url, headers=headers)
resp_content = resp.text

#解析数据
pre_re = re.compile(r'<li>.*?<span class="title">(?P<title>.*?)</span>.*?<span class="rating_num" property="v:average">(?P<average>.*?)</span>', re.S)
iter = pre_re.finditer(resp_content)

f = open("douban_top250.csv", mode="w")
csv_writer = csv.writer(f) # 将数据以 xxx,xxx 的方式进行输出

for it in iter:
    dic = it.groupdict()
    csv_writer.writerow(dic.values())
    
f.close()
print("over!")