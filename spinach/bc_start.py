from OneNineBC import OneNineBC
from PandaBC import PandaBC
import match_engine
import os
import bc_print


# 19 平台
oneNineBC = OneNineBC()
on_game_list = oneNineBC.crawling()
print("**********************************************************************")
print(f"19 平台比赛个数：{len(on_game_list)}")
# print(on_game_list)

# # panda 平台
pandaBC = PandaBC()
ob_game_list = pandaBC.crawling()
print("**********************************************************************")
print(f"ob 平台比赛个数：{len(ob_game_list)}")
# print(ob_game_list)
print(ob_game_list[0])
# pandaBC.auto_bet(ob_game_list[0], "qc_rq_list", -1.5, True, None, "15")

# # 匹配结果
match_result_list = match_engine.cal_odds(on_game_list, ob_game_list)
print("**********************************************************************")
print(f"ob 成功匹配个数：{len(match_result_list)}")
# print(match_result_list)

# 下注金额
bet_money = 15
is_bet_money_a = True
# 是否已经下注，通过该标志停止下注循环
is_bet = False
# 开始下注
for match_result in match_result_list:
    # 打印匹配结果
    print(f"ratio********{match_result['ratio']}")
    bc_print.print_match_result(match_result)
    if is_bet:
        continue
    # 语音提醒下注
    os.system('say "匹配成功！"')
    cmd = input("请确认是否自动下注 y/n：")
    if cmd == "y":
        pk = match_result["pk"]
        bet = match_result["bet"]
        zd = match_result["zd"]
        # game_a 核实赔率 ********************************
        game_a = match_result["game_a"]
        ratio_a = match_result["ratio_a"]
        iszd_a = False
        if zd == "game_a":
            iszd_a = True
        else:
            iszd_a = False
        print(f"{game_a['type']} 平台赔率: {ratio_a} 核对......")
        is_ok_a = oneNineBC.check_bet(game_a, pk, bet, iszd_a, ratio_a)
        if is_ok_a:
            bc_print.print_red(f"{game_a['type']} 赔率 OK!")
        else:
            # TODO 如果赔率变化不大，可根据用户选择继续执行下去
            bc_print.print_red(f"{game_a['type']} 赔率已改变，退出!")
            continue
        # game_b 核实赔率 **********************************
        game_b = match_result["game_b"]
        ratio_b = match_result["ratio_b"]
        if zd == "game_b":
            iszd_b = True
        else:
            iszd_b = False
        print(f"{game_b['type']} 平台赔率: {ratio_b} 核对......")
        is_ok_b = pandaBC.check_bet(game_b, pk, bet, iszd_b, ratio_b)
        if is_ok_b:
            bc_print.print_red(f"{game_b['type']} 赔率 OK!")
        else:
            # TODO 如果赔率变化不大，可根据用户选择继续执行下去
            bc_print.print_red(f"{game_b['type']} 赔率已改变，退出!")
            continue
        # 开始自动下注 ***********************************
        ratio = match_result["ratio"]
        if is_bet_money_a:
            bet_money_a = bet_money
            bet_money_b = int(bet_money * ratio_a - bet_money * ((ratio - 1) / 2.0))
        else:
            bet_money_b = bet_money
            bet_money_a = int(bet_money * ratio_b - bet_money * ((ratio - 1) / 2.0))
        print(f"{game_a['type']} 下注金额：{bet_money_a}, {game_b['type']} 下注金额：{bet_money_b}")
        # game_a 开始下注
        is_bet_ok_a = oneNineBC.auto_bet(bet_money_a)
        if is_bet_ok_a:
            is_bet = True
            bc_print.print_red(f"{game_a['type']} 下注成功！")
        else:
            bc_print.print_red(f"{game_a['type']} 下注失败！")
            continue
        is_bet_ok_b = pandaBC.auto_bet(game_b, iszd_b, bet_money_b)
        if is_bet_ok_b:
            bc_print.print_red(f"{game_b['type']} 下注成功！")
        else:
            bc_print.print_red(f"{game_b['type']} 下注失败！")
            continue