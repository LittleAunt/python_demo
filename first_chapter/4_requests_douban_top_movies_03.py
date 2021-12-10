import requests

url = "https://movie.douban.com/j/chart/top_list"
# 重新封装 get 参数
param = {
    "type": "24",
    "interval_id": "100:90",
    "action": "",
    "start": 0,
    "limit": 20
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'
}

resp = requests.get(url, params=param, headers=headers)

print(resp.json())
print(resp.request.headers)

resp.close() # 执行完请求后要关掉链接 => 默认 'Connection': 'keep-alive'
