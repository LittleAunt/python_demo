# 匹配结果后手动输入金额

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

# 是否循环，当下注成功应跳出循环
is_bet = False
while not is_bet:
    # 19 平台
    on_game_list = oneNineBC.crawling()
    print("**********************************************************************")
    print(f"19 平台比赛个数：{len(on_game_list)}")
    # panda 平台
    ob_game_list = pandaBC.crawling()
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
        # 语音提醒下注
        os.system('say "匹配成功！"')
        cmd = input("请确认是否自动下注 y/n：")
        if cmd.strip() == "y":
            game_a = match_result["game_a"]
            ratio_a = match_result["ratio_a"]
            game_b = match_result["game_b"]
            ratio_b = match_result["ratio_b"]
            # 输入金额 ********************************
            while True:
                platform = input("请输入需要下注平台 a/b：")
                if platform.strip() == 'a':
                    is_bet_money_a = True
                else:
                    is_bet_money_a = False
                money = input("请输入下注金额：")
                bet_money = int(money.strip())
                # 计算下注金额
                ratio = match_result["ratio"]
                if is_bet_money_a:
                    bet_money_a = bet_money
                    bet_money_b = int(bet_money * ratio_a -
                                      bet_money * ((ratio - 1) / 2.0 - REDUCE_MONEY))
                else:
                    bet_money_b = bet_money
                    bet_money_a = int(bet_money * ratio_b -
                                      bet_money * ((ratio - 1) / 2.0 - REDUCE_MONEY))
                print(
                    f"{game_a['type']} 下注金额：{bet_money_a}, {game_b['type']} 下注金额：{bet_money_b}")
                bet_confirm = input("确认是否自动下注 y/n：")
                if bet_confirm.strip() == 'y':
                    break
            # 赔率确认
            pk = match_result["pk"]
            bet = match_result["bet"]
            zd = match_result["zd"]
            # game_a 核实赔率 ********************************
            iszd_a = False
            if zd == "game_a":
                iszd_a = True
            else:
                iszd_a = False
            is_ok_a = oneNineBC.check_bet(game_a, pk, bet, iszd_a, ratio_a)
            if is_ok_a:
                bc_print.print_red(f"{game_a['type']} 赔率 OK!")
            else:
                check_confirm_a = input("赔率已改变! 是否继续下注 y/n：")
                if check_confirm_a.strip() != "y":
                    continue
            # game_b 核实赔率 **********************************
            if zd == "game_b":
                iszd_b = True
            else:
                iszd_b = False
            is_ok_b = pandaBC.check_bet(game_b, pk, bet, iszd_b, ratio_b)
            if is_ok_b:
                bc_print.print_red(f"{game_b['type']} 赔率 OK!")
            else:
                check_confirm_b = input("赔率已改变! 是否继续下注 y/n：")
                if check_confirm_b.strip() != "y":
                    continue
            # 开始自动下注 ***********************************
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
    # 睡眠 30 - 60 秒
    sleep_time = random.randint(60, 120)
    print(f"间隔时间：{sleep_time}")
    time.sleep(sleep_time)
