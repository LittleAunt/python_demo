import requests
from lxml import etree

# 请求
url = "https://nanjing.zbj.com/search/f/?kw=saas"
resp_main = requests.get(url) 
# 解析
html = etree.HTML(resp_main.text)
# 提取列表
results = html.xpath("/html/body/div[6]/div/div/div[2]/div[5]/div[1]/div")
for result in results:
    price = result.xpath('.//*[@id="utopia_widget_76"]/a[2]/div[2]/div[1]/span[1]/text()')[0].strip("¥")
    title = "saas".join(result.xpath('.//*[@id="utopia_widget_76"]/a[2]/div[2]/div[2]/p/text()'))
    com_name = result.xpath('./div/div/a[1]/div[1]/p/text()')[1].strip("\n")
    location = result.xpath('.//*[@id="utopia_widget_76"]/a[1]/div[1]/div/span/text()')[0]
    print(location)
    