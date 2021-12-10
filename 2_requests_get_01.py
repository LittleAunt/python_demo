import requests

query = input("请输入搜索内容：")

url = f"https://www.sogou.com/web?query={query}"
my_headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
}

resp = requests.get(url, headers=my_headers)
print(resp.text)

f = open("request_01.html", mode="w")
f.write(resp.text)
print("over!")