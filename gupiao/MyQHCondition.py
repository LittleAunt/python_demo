# -*- coding: utf-8 -*-

CP_MAX_MACD = 15 # 触碰反转 V 字中间 MACD 判断最大值
ZP_MAX_MACD = 15 # 未溢出，转多转空， V 字中间 MACD 判断最大值
Z2_MAX_MACD = 35 # 转2

# A 下穿 B，I 是指那一天的 index
def CROSSDOWN(A, B, I):
    if len(A) < 2:
        return False
    else:
        return A[I - 1] > B[I -1] and A[I] <= B[I]

# A 上穿 B，I 是指那一天的 index
def CROSSUP(A, B, I):
    if len(A) < 2:
        return False
    else:
        return A[I - 1] < B[I -1] and A[I] >= B[I]

# MACD 金叉，做多
def MACD_JC(DIFF, DEA, I):
    return CROSSUP(DIFF, DEA, I)

# MACD 死叉，做空
def MACD_SC(DIFF, DEA, I):
    return CROSSDOWN(DIFF, DEA, I)

# MACD 上溢出,平多
def MACD_UP_YC(MACD, DEA, I):
    cross = CROSSDOWN(MACD, DEA, I)
    return cross and MACD[I] > 0 and DEA[I] > 0

# MACD 下溢出,平空
def MACD_DOWN_YC(MACD, DEA, I):
    cross = CROSSUP(MACD, DEA, I)
    return cross and MACD[I] < 0 and DEA[I] < 0

# K线三连红，做多
def RED_K3(OPEN, CLOSE, I):
    if len(OPEN) < 3:
        return False
    else:
        day0 = CLOSE[I] - OPEN[I] > 0
        day1 = CLOSE[I - 1] - OPEN[I - 1] > 0
        day2 = CLOSE[I - 2] - OPEN[I - 2] > 0
        return day0 and day1 and day2

# K线三连绿，做空
def GREEN_K3(OPEN, CLOSE, I):
    if len(OPEN) < 3:
        return False
    else:
        day0 = CLOSE[I] - OPEN[I] < 0
        day1 = CLOSE[I - 1] - OPEN[I - 1] < 0
        day2 = CLOSE[I - 2] - OPEN[I - 2] < 0
        return day0 and day1 and day2

MACD_DIFF_RANGE = 0
# 三连绿后 MACD 线比前一天高, 转多
def MACD_UP_AFTER_GREEN_K3(OPEN, CLOSE, MACD, I):
    if len(MACD) < 2:
        return False
    else:
        green_k3 = GREEN_K3(OPEN, CLOSE, I - 1)
        green_k3_1 = GREEN_K3(OPEN, CLOSE, I - 2)
        c_macd = MACD[I]
        p_macd = MACD[I - 1]
        if c_macd > 0 and p_macd > 0:
            return (green_k3) and c_macd - p_macd > MACD_DIFF_RANGE
        # elif c_macd < 0 and p_macd < 0:
        #     return (green_k3 or green_k3_1) and c_macd - p_macd > MACD_DIFF_RANGE
            

# 三连红后 MACD 线比前一天低，转空
def MACD_DOWN_AFTER_RED_K3(OPEN, CLOSE, MACD, I):
    if len(MACD) < 2:
        return False
    else :
        red_k3 = RED_K3(OPEN, CLOSE, I - 1)
        red_k3_1 = RED_K3(OPEN, CLOSE, I - 2)
        c_macd = MACD[I]
        p_macd = MACD[I - 1]
        if c_macd < 0 and p_macd < 0:
            return (red_k3) and c_macd - p_macd < -1 * MACD_DIFF_RANGE
        # elif c_macd > 0 and p_macd > 0:
        #     return (red_k3 or red_k3_1) and c_macd - p_macd < -1 * MACD_DIFF_RANGE

# MACD首次大于前一天，MACD未溢出，转多
def MACD_UP_V(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return MACD[I] > DEA[I] and MACD[I] > 0 and MACD[I - 1] > 0 and MACD[I] - MACD[I - 1] > MACD_DIFF_RANGE and MACD[I - 1] - MACD[I - 2] < -1 * MACD_DIFF_RANGE and MACD[I - 1] > ZP_MAX_MACD

# MACD首次小于前一天，MACD未溢出，转空
def MACD_DOWN_V(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return MACD[I] < DEA[I] and MACD[I] < 0 and MACD[I - 1] < 0 and MACD[I] - MACD[I - 1] < -1 * MACD_DIFF_RANGE and MACD[I - 1] - MACD[I - 2] > MACD_DIFF_RANGE and MACD[I - 1] < -1 * ZP_MAX_MACD

# 触碰反转做多。MACD 呈 V 字型，中间值小于 12。相当于 DIFF DEA 差点碰到一起。触多
def MACD_UP_V_CP(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return MACD[I] > 0 and MACD[I - 1] > 0 and MACD[I] - MACD[I - 1] > MACD_DIFF_RANGE and MACD[I - 1] - MACD[I - 2] < -1 * MACD_DIFF_RANGE and MACD[I - 1] < CP_MAX_MACD and DIFF[I] > 0 and DEA[I] > 0 

# 触碰反转做空。触空
def MACD_DOWN_V_CP(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return MACD[I] < 0 and MACD[I - 1] < 0 and MACD[I] - MACD[I - 1] < -1 * MACD_DIFF_RANGE and MACD[I - 1] - MACD[I - 2] > MACD_DIFF_RANGE and MACD[I - 1] > -1 * CP_MAX_MACD and DIFF[I] < 0 and DEA[I] < 0 

# 转空2，下跌趋势下，出现金叉，但 MACD 短时间反转
def FZ2_K(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return DIFF[I] < 0 and DEA[I] < 0 and MACD[I] > 0 and MACD[I - 1] > 0 and MACD[I - 2] > 0 and MACD[I] < MACD[I - 1] and MACD[I - 1] > MACD[I - 2] and MACD[I - 1] < Z2_MAX_MACD

# 转多2，上涨趋势下，出现死叉，但 MACD 短时间反转
def FZ2_D(MACD, DIFF, DEA, I):
    if len(MACD) < 3:
        return False
    else:
        return DIFF[I] > 0 and DEA[I] > 0 and MACD[I] < 0 and MACD[I - 1] < 0 and MACD[I - 2] < 0 and MACD[I] > MACD[I - 1] and MACD[I - 1] < MACD[I - 2] and MACD[I - 1] > -1 * Z2_MAX_MACD