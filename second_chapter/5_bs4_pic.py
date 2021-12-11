import requests
from bs4 import BeautifulSoup
import time

url = "https://www.umei.cc/bizhitupian/weimeibizhi/"
resp = requests.get(url)
resp.encoding = "utf-8"
resp.close()
# 提取图片列表
page = BeautifulSoup(resp.text, "html.parser")
pic_list = page.find("div", class_="TypeList").find_all("a")
domain = "https://www.umei.cc"
# 获取图片下载链接
for pic in pic_list:
    href = domain + pic.get("href")
    child_resp = requests.get(href)
    child_resp.close()
    child_resp.encoding = "utf-8"
    child_page = BeautifulSoup(child_resp.text, "html.parser")
    child_img = child_page.find("div", class_="ImageBody").find("img")
    img_src = child_img.get("src")
    # 下载图片
    img_resp = requests.get(img_src)
    img_resp.close()
    # img_resp.content 为字节内容
    img_name = img_src.split("/")[-1] # 截取 url 最后 / 的内容
    # wb 以字节的方式写入文件, 注意：img是运行该脚本时终端所在的目录下的img文件夹，而不是脚本所在目录下的 img
    with open("img/"+img_name, mode="wb") as f:
        f.write(img_resp.content)
        print("download: " + img_name + " finished!")
    time.sleep(1)
print("over!")
    