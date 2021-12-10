import requests

url = "https://fanyi.baidu.com/sug"
word = input("请输入需要翻译的单词：")

form_data = {
    "kw": word
}

resp = requests.post(url, data=form_data)

print(resp.json()) # 将服务器返回结果直接处理成 json