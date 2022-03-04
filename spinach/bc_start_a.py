# 提前输入金额

from OneNineBC import OneNineBC
from PandaBC import PandaBC
import match_engine
import os
import bc_print
import random
import time
from config import REDUCE_MONEY

oneNineBC = OneNineBC()
pandaBC = PandaBC()

platform = input("请输入需要下注平台 a/b：")
if platform.strip() == 'a':
    is_bet_money_a = True
else:
    is_bet_money_a = False
money = input("请输入下注金额：")
bet_money = int(money.strip())
print(f"平台a：{is_bet_money_a}, 金额：{bet_money}")
# 是否循环，当下注成功应跳出循环
is_bet = False
while not is_bet:
    # 19 平台
    on_game_list = oneNineBC.crawling()
    if on_game_list == None:
        bc_print.print_red("19 数据获取失败！")
        continue
    print("**********************************************************************")
    print(f"19 平台比赛个数：{len(on_game_list)}")
    # panda 平台
    ob_game_list = pandaBC.crawling()
    if ob_game_list == None:
        bc_print.print_red("ob 数据获取失败！")
        continue
    print("**********************************************************************")
    print(f"ob 平台比赛个数：{len(ob_game_list)}")
    # 匹配结果
    match_result_list = match_engine.cal_odds(on_game_list, ob_game_list)
    print("**********************************************************************")
    print(f"成功匹配个数：{len(match_result_list)}")
    # 开始下注
    for match_result in match_result_list:
        # 打印匹配结果
        bc_print.print_match_result(match_result)
        if is_bet:
            continue
        # 打印金额
        ratio = match_result["ratio"]
        ratio_a = match_result["ratio_a"]
        game_a = match_result["game_a"]
        ratio_b = match_result["ratio_b"]
        game_b = match_result["game_b"]
        if is_bet_money_a:
            bet_money_a = bet_money
            bet_money_b = int(bet_money_a * (ratio_a + 1) / (ratio_b + 1)) - REDUCE_MONEY
        else:
            bet_money_b = bet_money
            bet_money_a = int(bet_money_b * (ratio_b + 1) / (ratio_a + 1)) - REDUCE_MONEY
        print(
            f"{game_a['type']} 下注金额：{bet_money_a}, {game_b['type']} 下注金额：{bet_money_b}")
        # 语音提醒下注
        os.system('say "匹配成功！"')
        cmd = input("请确认是否自动下注 y/n：")
        if cmd.strip() == "y":
            pk = match_result["pk"]
            bet = match_result["bet"]
            zd = match_result["zd"]
            # game_a 核实赔率 ********************************
            iszd_a = False
            if zd == "game_a":
                iszd_a = True
            else:
                iszd_a = False
            is_ok_a = oneNineBC.check_bet(game_a, pk, bet, iszd_a, ratio_a, bet_money_a)
            if is_ok_a:
                bc_print.print_red(f"{game_a['type']} 赔率 OK!")
            else:
                bc_print.print_red(f"{game_a['type']} 赔率核对失败!")
                continue
                # check_confirm_a = input("赔率核对失败! 是否继续下注 y/n：")
                # if check_confirm_a.strip() != "y":
                #     continue
            # game_b 核实赔率 **********************************
            if zd == "game_b":
                iszd_b = True
            else:
                iszd_b = False
            is_ok_b = pandaBC.check_bet(game_b, pk, bet, iszd_b, ratio_b, bet_money_b)
            if is_ok_b:
                bc_print.print_red(f"{game_b['type']} 赔率 OK!")
            else:
                bc_print.print_red(f"{game_b['type']} 赔率核对失败!")
                continue
                # check_confirm_b = input("赔率核对失败! 是否继续下注 y/n：")
                # if check_confirm_b.strip() != "y":
                #     continue
            continue
            # 开始自动下注 ***********************************
            # a 
            is_bet_ok_a = oneNineBC.auto_bet(bet_money_a)
            if is_bet_ok_a:
                bc_print.print_red(f"{game_a['type']} 下注成功！")
            else:
                bc_print.print_red(f"{game_a['type']} 下注失败！")
                continue
            # b
            is_bet_ok_b = pandaBC.auto_bet(game_b, iszd_b, bet_money_b)
            if is_bet_ok_b:
                is_bet = True
                bc_print.print_red(f"{game_b['type']} 下注成功！")
            else:
                bc_print.print_red(f"{game_b['type']} 下注失败！")
                continue
            
            # is_bet_ok_a = oneNineBC.auto_bet(bet_money_a)         
            # if is_bet_ok_a:
            #     is_bet = True
            #     bc_print.print_red(f"{game_a['type']} 下注成功！")
            # else:
            #     # 下注失败，再尝试一次下注
            #     again_confirm_a = input("下注失败! 是否重新下注 y/n：")
            #     if again_confirm_a.strip() == "y":
            #         again_is_ok_a = oneNineBC.check_bet(game_a, pk, bet, iszd_a, ratio_a, bet_money_a)
            #         again_check_confirm_a = input("是否继续下注 y/n：")
            #         if again_check_confirm_a.strip() == "y":
            #             again_is_bet_ok_a = oneNineBC.auto_bet(bet_money_a)
            #             if again_is_bet_ok_a:
            #                 bc_print.print_red(f"{game_a['type']} 下注成功！")
            #             else:
            #                 bc_print.print_red(f"{game_a['type']} 下注失败！")
            #     else:
            #         continue
    # 睡眠 30 - 60 秒
    sleep_time = random.randint(30, 60)
    print(f"间隔时间：{sleep_time}")
    time.sleep(30)
