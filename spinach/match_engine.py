import os
from config import TARGET_ODDS, ONLY_WIN_OR_LOSE

match_result_list = [] # 匹配成功的结果列表
"""
匹配的结果字段
{
    "game_a": game_a, # a 平台的一场比赛
    "game_b": game_b, # b 平台的一场比赛
    "pk": pk, # 哪个盘口
    "ratio": , # 实际赔率，a、b 平台的赔率乘积。用来排序，最大赔率的显示在最上面
    "ratio_a": , # a 平台的赔率
    "ratio_b": , # b 平台的赔率
}
"""
    
def print_red(p_str):
    print('\033[1;31;40m ' + p_str + ' \033[0m')
    # os.system('say "匹配成功！"')


# 盘口数值转换，用于 log 输出
def convert_game_type(type_f):
    type_str = ''
    if type_f % 0.5 != 0:
        if type_f > 0:
            type_str = str(type_f - 0.25) + '/' + str(type_f + 0.25)
        else:
            type_str = '-' + str(abs(type_f) - 0.25) + '/' + str(abs(type_f) + 0.25)
    else:
        type_str = str(type_f)
    return type_str

# 盘口对比
def compare_pk(game1, game2, pk, list1, list2):
    for list1_key, list1_value_str in list1.items():
        if list1_key not in list2:
            continue
        # 只匹配 0.5、2.5 这种绝对输赢的盘口，不匹配存在平局或输一半情况的盘口
        if ONLY_WIN_OR_LOSE:
            # 截取小数点后面的数字
            list1_key_str = str(list1_key)
            list1_key_point = float(list1_key_str[list1_key_str.index('.') + 1:])
            if list1_key_point != 5:
                continue
        # 提取两个平台盘口对应的赔率数值
        list2_value_str = list2[list1_key]
        list1_values = list1_value_str.split(',')
        list2_values = list2_value_str.split(',')
        # 赔率对比 
        ratio1 = float(list1_values[0]) * float(list2_values[1])
        ratio2 = float(list1_values[1]) * float(list2_values[0])
        match_result = {}
        if ratio1 >= TARGET_ODDS:
            match_result["game_a"] = game1
            match_result["game_b"] = game2
            match_result["pk"] = pk
            match_result["ratio"] = ratio1
            match_result["ratio_a"] = float(list1_values[0])
            match_result["ratio_b"] = float(list2_values[1])
            match_result_list.append(match_result)
        if ratio2 >= TARGET_ODDS:
            match_result["game_a"] = game1
            match_result["game_b"] = game2
            match_result["pk"] = pk
            match_result["ratio"] = ratio1
            match_result["ratio_a"] = float(list1_values[1])
            match_result["ratio_b"] = float(list2_values[0])
            match_result_list.append(match_result)
            

# 计算两个平台比赛的赔率
def cal_game(game1, game2):
    # 全场让球赔率计算
    if 'qc_rq_list' in game1 and 'qc_rq_list' in game2:
        game1_qc_rq = game1['qc_rq_list']
        game2_qc_rq = game2['qc_rq_list']
        compare_pk(game1, game2, '全场 让球', game1_qc_rq, game2_qc_rq)
    # 全场大小赔率计算
    if 'qc_dx_list' in game1 and 'qc_dx_list' in game2:
        game1_qc_dx = game1['qc_dx_list']
        game2_qc_dx = game2['qc_dx_list']
        compare_pk(game1, game2, '全场 大/小', game1_qc_dx, game2_qc_dx)
    # 半场让球
    if 'bc_rq_list' in game1 and 'bc_rq_list' in game2:
        game1_bc_rq = game1['bc_rq_list']
        game2_bc_rq = game2['bc_rq_list']
        compare_pk(game1, game2, '上半场 让球', game1_bc_rq, game2_bc_rq)
    # 半场大小
    if 'bc_dx_list' in game1 and 'bc_dx_list' in game2:
        game1_bc_dx = game1['bc_dx_list']
        game2_bc_dx = game2['bc_dx_list']
        compare_pk(game1, game2, '上半场 大/小', game1_bc_dx, game2_bc_dx)
        
def cal_odds(game_a_list, game_b_list):
    print("**********************************************************************")
    match_count = 0 # 共匹配了多少场
    match_result_list.clear() # 匹配成功的结果列表
    for game_a in game_a_list:
        # 是否匹配对应比赛
        matched = False
        for game_b in game_b_list:
            # 优化名称，剔除不利字符
            name_a_team_1 = game_a['team_name_1'].replace(' ', '').replace("[", "(").replace("]", ")").replace("女", "女")
            name_a_team_2 = game_a['team_name_2'].replace(' ', '').replace("[", "(").replace("]", ")").replace("女", "女")
            name_b_team_1 = game_b['team_name_1'].replace(' ', '').replace("[", "(").replace("]", ")").replace("女", "女")
            name_b_team_2 = game_b['team_name_2'].replace(' ', '').replace("[", "(").replace("]", ")").replace("女", "女")  
            # 比赛比对成功，开始计算赔率
            if game_a['team_id_1'] == game_b['team_id_1'] or game_a['team_id_2'] == game_b['team_id_2']:
                matched = True
                break
            elif (name_a_team_1 == name_b_team_1 or name_a_team_2 == name_b_team_2):
                matched = True
                break
        if matched:
            cal_game(game_a, game_b)
            match_count = match_count + 1
        else:
            print('NO MATCHED! {0} {1} 比赛队伍： {2} -> {3} | ID: [{4},{5}]'.format(game_a['type'],
                                                                                game_a["league_name"],
                                                                                game_a['team_name_1'],
                                                                                game_a['team_name_2'],
                                                                                game_a['team_id_1'],
                                                                                game_a['team_id_2']))
    print(f'匹配了 {match_count} 场比赛')
    return match_result_list
