from OneNineBC import OneNineBC

# 19 平台
oneNineBC = OneNineBC()
on_json = oneNineBC.crawling() # 爬取
on_game_list = oneNineBC.parse(on_json) # 解析成比赛列表
print(on_game_list)