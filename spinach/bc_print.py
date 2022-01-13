
def print_red(p_str):
    print('\033[1;31;40m ' + p_str + ' \033[0m')

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

def convert_pk(pk_type):
    if pk_type == "qc_rq_list":
        return "全场让球"
    if pk_type == "qc_dx_list":
        return "全场大小"
    if pk_type == "bc_rq_list":
        return "半场让球"
    if pk_type == "bc_dx_list":
        return "半场大小"
    
# 打印匹配结果
def print_match_result(match_result):
    print("**********************************************************************")
    # 打印当前赔率
    ratio = match_result["ratio"]
    print_red(f"当前赔率: {ratio}")
    bet_type = convert_game_type(match_result["bet"])
    # 打印 game_a 信息
    game_a = match_result["game_a"]
    type_a = game_a["type"]
    time_a = game_a["time"]
    ls_a = game_a["league_name"]
    team_a_1 = game_a["team_name_1"]
    team_a_2 = game_a["team_name_2"]
    pk = convert_pk(match_result["pk"])
    if match_result["zd"] == "game_a":
        zk_a = "主"
    else:
        zk_a = "客"
    ratio_a = match_result["ratio_a"]
    print_red(f"{type_a} -》{time_a} {ls_a} -》{team_a_1} : {team_a_2} -》{pk} {bet_type} ({zk_a}) : {ratio_a}")
    # 打印 game_b 信息
    game_b = match_result["game_b"]
    type_b = game_b["type"]
    time_b = game_b["time"]
    ls_b = game_b["league_name"]
    team_b_1 = game_b["team_name_1"]
    team_b_2 = game_b["team_name_2"]
    pk = convert_pk(match_result["pk"])
    if match_result["zd"] == "game_b":
        zk_b = "主"
    else:
        zk_b = "客"
    ratio_b = match_result["ratio_b"]
    print_red(f"{type_b} -》{time_b} {ls_b} -》{team_b_1} : {team_b_2} -》{pk} {bet_type} ({zk_b}) : {ratio_b}")