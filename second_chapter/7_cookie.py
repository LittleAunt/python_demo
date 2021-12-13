import requests

session = requests.session()
# 登录
url = "https://passport.17k.com/ck/user/login"
data = {
    "loginName": "15295032087",
    "password": "abc123_"
}
resp = session.post(url, data=data)
# 拿书架数据
resp_books = session.get("https://user.17k.com/ck/author/shelf?page=1&appKey=2406394919")
print(resp_books.json())

# 手动设置 cookie
# resp_books = requests.get("https://user.17k.com/ck/author/shelf?page=1&appKey=2406394919", headers = {
#     "Cookie": "GUID=41daea1c-a0cd-48c5-923b-c1b42aaff39b; sajssdk_2015_cross_new_user=1; c_channel=0; c_csc=web; accessToken=avatarUrl%3Dhttps%253A%252F%252Fcdn.static.17k.com%252Fuser%252Favatar%252F17%252F57%252F84%252F86778457.jpg-88x88%253Fv%253D1639363140000%26id%3D86778457%26nickname%3D%25E4%25B9%25A6%25E5%258F%258B6ljB00467%26e%3D1654918283%26s%3D2c771a21678bede0; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2286778457%22%2C%22%24device_id%22%3A%2217db1a543c8642-04b348babb3d6f-1f396452-1484784-17db1a543c92eb%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%2C%22first_id%22%3A%2241daea1c-a0cd-48c5-923b-c1b42aaff39b%22%7D"
# })
# print(resp_books.json())
