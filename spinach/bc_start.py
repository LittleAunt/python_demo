from OneNineBC import OneNineBC
from PandaBC import PandaBC
import match_engine

# 19 平台
oneNineBC = OneNineBC()
# on_game_list = oneNineBC.crawling()  # 爬取
# print("**********************************************************************")
# print(f"19 平台比赛个数：{len(on_game_list)}")
# # print(on_game_list)
oneNineBC.auto_bet("","","","","")

# # panda 平台
# pandaBC = PandaBC()
# ob_game_list = pandaBC.crawling()
# print("**********************************************************************")
# print(f"ob 平台比赛个数：{len(ob_game_list)}")
# # print(ob_game_list)

# # 匹配结果
# match_result_list = match_engine.cal_odds(on_game_list, ob_game_list)
# print("**********************************************************************")
# print(f"ob 成功匹配个数：{len(match_result_list)}")
# print(match_result_list)
