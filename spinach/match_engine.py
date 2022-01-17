from config import TARGET_ODDS, ONLY_WIN_OR_LOSE
import re

match_result_list = [] # 匹配成功的结果列表
"""
匹配的结果字段
{
    "game_a": game_a, # a 平台的一场比赛
    "game_b": game_b, # b 平台的一场比赛
    "pk": pk, # 哪个盘口
    "bet": "", # 哪个赔率盘
    "zd": "", 匹配结果中的主队是
    "kd": "", 匹配结果中的客队是
    "ratio": , # 实际赔率，a、b 平台的赔率乘积。用来排序，最大赔率的显示在最上面
    "ratio_a": , # a 平台的赔率
    "ratio_b": , # b 平台的赔率
}
"""

# 盘口对比
def compare_pk(game1, game2, pk, list1, list2):
    for list1_key, list1_value_str in list1.items():
        if list1_key not in list2:
            continue
        # 只匹配 0.5、2.5 这种绝对输赢的盘口，不匹配存在平局或输一半情况的盘口
        if ONLY_WIN_OR_LOSE:
            # 以小数点拆分，小数点后为 5 才继续对比
            list1_key_str = str(list1_key)
            list1_key_values = list1_key_str.split(".")
            if len(list1_key_values) != 2 or list1_key_values[1] != '5':
                continue
        # 提取两个平台盘口对应的赔率数值
        list2_value_str = list2[list1_key]
        list1_values = list1_value_str.split(',')
        list2_values = list2_value_str.split(',')
        # 赔率对比 
        ratio1 = float(list1_values[0]) * float(list2_values[1])
        ratio2 = float(list1_values[1]) * float(list2_values[0])
        match_result = {}
        # 不仅赔率乘积要大于预期，且双方的赔率都不能小于 0.5（低于0.5的基本比赛快结束，下注易失败）
        if ratio1 >= TARGET_ODDS and float(list1_values[0]) >= 0.5 and float(list2_values[1]) >= 0.5:
            match_result["game_a"] = game1
            match_result["game_b"] = game2
            match_result["pk"] = pk
            match_result["bet"] = list1_key
            match_result["zd"] = "game_a"
            match_result["kd"] = "game_b"
            match_result["ratio"] = ratio1
            match_result["ratio_a"] = float(list1_values[0])
            match_result["ratio_b"] = float(list2_values[1])
            match_result_list.append(match_result)
        if ratio2 >= TARGET_ODDS and float(list1_values[1]) >= 0.5 and float(list2_values[0]) >= 0.5:
            match_result["game_a"] = game1
            match_result["game_b"] = game2
            match_result["pk"] = pk
            match_result["bet"] = list1_key
            match_result["zd"] = "game_b"
            match_result["kd"] = "game_a"
            match_result["ratio"] = ratio2
            match_result["ratio_a"] = float(list1_values[1])
            match_result["ratio_b"] = float(list2_values[0])
            match_result_list.append(match_result)
            

# 计算两个平台比赛的赔率
def cal_game(game1, game2):
    # 全场让球赔率计算
    if 'qc_rq_list' in game1 and 'qc_rq_list' in game2:
        game1_qc_rq = game1['qc_rq_list']
        game2_qc_rq = game2['qc_rq_list']
        compare_pk(game1, game2, 'qc_rq_list', game1_qc_rq, game2_qc_rq)
    # 全场大小赔率计算
    if 'qc_dx_list' in game1 and 'qc_dx_list' in game2:
        game1_qc_dx = game1['qc_dx_list']
        game2_qc_dx = game2['qc_dx_list']
        compare_pk(game1, game2, 'qc_dx_list', game1_qc_dx, game2_qc_dx)
    # 半场让球
    if 'bc_rq_list' in game1 and 'bc_rq_list' in game2:
        game1_bc_rq = game1['bc_rq_list']
        game2_bc_rq = game2['bc_rq_list']
        compare_pk(game1, game2, 'bc_rq_list', game1_bc_rq, game2_bc_rq)
    # 半场大小
    if 'bc_dx_list' in game1 and 'bc_dx_list' in game2:
        game1_bc_dx = game1['bc_dx_list']
        game2_bc_dx = game2['bc_dx_list']
        compare_pk(game1, game2, 'bc_dx_list', game1_bc_dx, game2_bc_dx)
        
# 模糊匹配
def fuzzy_matching2(array1, array2):
    index = -1
    count = 0
    for a1 in array1:
        if a1 in array2:
            c_index = array2.index(a1)
            if c_index > index:
                index = c_index
                count += 1
    return count

# 模糊匹配，两个字符串之间进行单个字符对比，如果长度小的字符的一半对比成功，则默认相等
# 1.提取中文；2.大于或等于一半的字符；3.至少两个字符
def fuzzy_matching(str1, str2, accuracy):
    # 提取中文字符，只对比中文字符
    strArray1 = re.findall(r"[\u4e00-\u9fa5]", str1)
    strArray2 = re.findall(r"[\u4e00-\u9fa5]", str2)
    # 遍历短的数组
    if len(strArray1) > len(strArray2):
        match_count = fuzzy_matching2(strArray2, strArray1)
        if match_count > 1 and match_count >= len(strArray2) * accuracy:
            # print(f'模糊匹配成功 {str1}, {str2}')
            return True
    else:
        match_count = fuzzy_matching2(strArray1, strArray2)
        if match_count > 1 and match_count >= len(strArray1) * accuracy:
            # print(f'模糊匹配成功 {str1}, {str2}')
            return True 
    return False
        
def cal_odds(game_a_list, game_b_list):
    print("**********************************************************************")
    match_count = 0 # 共匹配了多少场
    match_result_list.clear() # 匹配成功的结果列表
    for game_a in game_a_list:
        # 是否匹配对应比赛
        matched = False
        for game_b in game_b_list:
            # if game_a['team_name_1'] == '塞维利亚 [女]':
            #     continue
            if game_a['time'] != game_b['time']:
                continue
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
            # 模糊匹配，联赛比配成功，且比赛名匹配成功
            league_name_a = game_a["league_name"].replace('联赛', '').replace('杯', '').replace('级', '').replace('級', '')
            league_name_b = game_b["league_name"].replace('联赛', '').replace('杯', '').replace('级', '').replace('級', '')
            if fuzzy_matching(league_name_a, league_name_b, 1):
                if fuzzy_matching(name_a_team_1, name_b_team_1, 0.7) or fuzzy_matching(name_a_team_2, name_b_team_2, 0.7):
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
    # 按赔率从高到低排序
    match_result_sort_list = sorted(match_result_list, reverse=True, key=lambda result:result["ratio"])
    return match_result_sort_list
