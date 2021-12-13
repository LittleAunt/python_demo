import requests

# 代理 ip
proxi = {
    "https": "https://165.232.185.149:3128"
} 

resp = requests.get("https://www.baidu.com", proxies=proxi)
resp.encoding = "utf-8"
print(resp.text)

