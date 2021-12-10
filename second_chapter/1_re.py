import re

list = re.findall(r"\d+", "my phone number is 11010,12345")
print(list)

# 迭代器,效率比上面高
it = re.finditer(r"\d+", "my phone number is 11010,12345")
for i in it:
    print(i.group())
    
# 搜索并返回一个结果
s = re.search(r"\d+", "my phone number is 11010,12345")
print(s.group())

# match 是从头开始匹配 => 相当于 ^
s = re.match(r"\d+", "123my phone number is 11010,12345")
print(s.group())

# 预加载
obj = re.compile(r"\d+")
it = obj.finditer("my phone number is 11010,12345")
for i in it:
    print(i.group())
    
# 事例
s = """
<div class='a'><span id='1'>周杰伦</span></div>
<div class='b'><span id='2'>林俊杰</span></div>
"""
# (?P<分组名称>正则) 可单独从正则匹配结果提取分组内容
pre_re = re.compile(r"<div class='.*?'><span id='\d+'>(?P<name>.*?)</span></div>", re.S) # re.S 表示 . 匹配换行符
iter = pre_re.finditer(s)
for i in iter:
    print(i.group("name"))