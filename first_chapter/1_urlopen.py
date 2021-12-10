from urllib.request import urlopen
 
url = "http://www.baidu.com"
resp = urlopen(url)
# print(resp.read().decode("utf-8")) #字节转字符串输出
#打开文件，输出
with open("mybaidu.html", mode="w") as f:
    f.write(resp.read().decode("utf-8"))
    print("over!")
    f.close()