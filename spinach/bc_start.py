from OneNineBC import OneNineBC
from PandaBC import PandaBC

# 19 平台
oneNineBC = OneNineBC()
on_game_list = oneNineBC.crawling() # 爬取
print(on_game_list)

# panda 平台
pandaBC = PandaBC()
ob_game_list = pandaBC.crawling()
print(ob_game_list)