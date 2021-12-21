from OneNineBC import OneNineBC
from PandaBC import PandaBC
import match_engine

# 19 平台
# oneNineBC = OneNineBC()
# on_game_list = oneNineBC.crawling()  # 爬取
# print("**********************************************************************")
# print(f"19 平台比赛个数：{len(on_game_list)}")
# print(on_game_list)

# # panda 平台
pandaBC = PandaBC()
ob_game_list = pandaBC.crawling()
print("**********************************************************************")
print(f"ob 平台比赛个数：{len(ob_game_list)}")
# print(ob_game_list)
print(ob_game_list[0])
pandaBC.auto_bet(ob_game_list[0], "qc_rq_list", -1.5, True, None, "15")

# # 匹配结果
# match_result_list = match_engine.cal_odds(on_game_list, ob_game_list)
# print("**********************************************************************")
# print(f"ob 成功匹配个数：{len(match_result_list)}")
# print(match_result_list)

# 开始下注
# for match_result in match_result_list:
#     cmd = input("请确认是否自动下注 y/n：")
#     if cmd == "y":
#         print("开始自动下注 19 平台")
#         game_a = match_result["game_a"]
#         pk = match_result["pk"]
#         bet = match_result["bet"]
#         zd = match_result["zd"]
#         iszd = False
#         if zd == "game_a":
#             iszd = True
#         else:
#             iszd = False
#         ratio = match_result["ratio"]
#         oneNineBC.auto_bet(game_a, pk, bet, iszd, ratio, money)