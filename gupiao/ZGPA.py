# -*- coding: utf-8 -*-
from  Ashare import *
from  MyTT import * 
from ProCondition import *
from datetime import timedelta
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


STOCK_CODE = "000001" # 模拟的股票代码
STOCK_START_DATE = "2024-01-01"
STOCK_END_DATE = "2024-08-01"

# 每笔投资记录
RECORD_DATE = "record_date" # 交易日期
RECORD_PRICE = "record_price" # 交易价格
RECORD_PROFIT = "record_profit" # 收益

# 匹配的条件记录
CONDITION_DATE = "condition_date"
CONDITION_MSG = "condition_msg"

# 交易类型。0,1,2 分别代表做多、做空、平仓
INVEST_TYPE = "invest_type" 
TYPE_D = 0
TYPE_P = 2


def print_red(p_str):
    print('\033[1;31;40m' + p_str + '\033[0m')
    
# 计算收益。根据 duo 判断是做多还是空
def cal_profit(last_price, cur_price, buy_count):
    last_amount = last_price * buy_count * 100
    change = (cur_price - last_price) / last_price
    return round(last_amount * change, 2)
    
# 条件判断，是否满足自定义指标要求
def condition_matched(con_mets, cur_date, M_DIFF, M_DEA, M_MACD, OPEN, CLOSE, i):
    matched = False
    # 1. MACD 金叉、死叉
    if MACD_JC(M_DIFF, M_DEA, i):
        con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "JC", INVEST_TYPE: TYPE_D}) # 金叉
        matched = True
    if MACD_SC(M_DIFF, M_DEA, i):
        con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "SC", INVEST_TYPE: TYPE_P}) # 死叉
        matched = True
        # 2. MACD 溢出
    # if MACD_UP_YC(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "PD", INVEST_TYPE: TYPE_P}) # 平多
    #     matched = True
    # if MACD_DOWN_YC(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "PK", INVEST_TYPE: TYPE_P}) # 平空
    #     matched = True
    # 3. 三连红、三连绿
    # if RED_K3(M_DIFF, OPEN, CLOSE, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "3D", INVEST_TYPE: TYPE_D}) # 三多
    #     matched = True
    # if GREEN_K3(M_DIFF, OPEN, CLOSE, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "3K", INVEST_TYPE: TYPE_P}) # 三空
    #     matched = True
    # # 4. 反转做多、做空。三连绿后，MACD线比前一天高               (需设定范围，高 0.1 也是高)
    # if MACD_UP_AFTER_GREEN_K3(M_DIFF, OPEN, CLOSE, M_MACD, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "ZD0", INVEST_TYPE: TYPE_D}) # 转多0
    #     matched = True
    # if MACD_DOWN_AFTER_RED_K3(M_DIFF, OPEN, CLOSE, M_MACD, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "ZK0", INVEST_TYPE: TYPE_P}) # 转空0
    #     matched = True
    # # 5. 反转做多、做空。MACD首次大于前一天，MACD未溢出           (需设定范围，高 0.1 也是高)
    # if MACD_UP_V(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "ZD1", INVEST_TYPE: TYPE_D}) # 转多1
    #     matched = True
    # if MACD_DOWN_V(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "ZK1", INVEST_TYPE: TYPE_P}) # 转空1
    #     matched = True
    # # 6. 触碰反转做多，做空。MACD 呈 V 字型，中间值小于 12。相当于 DIFF DEA 差点碰到一起。 (需设定范围，高 0.1 也是高)
    # if MACD_UP_V_CP(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "CD", INVEST_TYPE: TYPE_D}) # 触多
    #     matched = True
    # if MACD_DOWN_V_CP(M_MACD, M_DIFF, M_DEA, i):
    #     con_mets.append({CONDITION_DATE: cur_date, CONDITION_MSG: "CK", INVEST_TYPE: TYPE_P}) # 触空
    #     matched = True
    return matched

# 添加一条交易记录
def add_record(records, date, price, type, buy_count):
    # 列表为空，直接插入一条交易记录
    if len(records) == 0:
        records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: 0})
    else: # 取最后一次交易记录，与当前交易进行对比计算收益
        last_record = records[-1]
        # 1. 当前是做多
        if type == TYPE_D:
            if last_record[INVEST_TYPE] == TYPE_P:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: 0})
        # 2. 当前是做平
        elif type == TYPE_P:
            if last_record[INVEST_TYPE] == TYPE_D:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count)})

    
def simulated_invest(code, sd, ed, buy_count, show_table):
    records = []
    con_mets = []
    # 将字符串转换为日期对象
    start_date = pd.to_datetime(sd)
    end_date = pd.to_datetime(ed)
    # 计算天数差
    days_count = (end_date - start_date).days + 200
    df = get_price(f'sh{code}',frequency='1d',count=days_count, end_date=ed, tx_channel=True)
    OPEN = df.open.values # 开盘列表
    CLOSE = df.close.values # 收盘列表
    # 过滤想要的日期时间段数据
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df[mask]
    # MACD 三项指标
    MM_DIFF, MM_DEA, MM_MACD = MACD(CLOSE, 12, 26, 9)
    # 截取倒数多少条数据
    last_count = -1 * len(filtered_df)
    M_DIFF = MM_DIFF[last_count:]
    M_DEA = MM_DEA[last_count:]
    M_MACD = MM_MACD[last_count:]
    # 遍历进行模拟买卖
    for i in range(0, len(filtered_df)):
        cur_row = filtered_df.iloc[i]
        cur_date = filtered_df.index[i]
        # 匹配买卖点
        matched = condition_matched(con_mets, cur_date, M_DIFF, M_DEA, M_MACD, OPEN, CLOSE, i)
        if matched:
            add_record(records, cur_date, cur_row.close, con_mets[-1][INVEST_TYPE], buy_count)
    # 取最后一笔交易如果没平仓，直接平仓
    last_date = filtered_df.index[-1]
    last_row = filtered_df.iloc[-1]
    if len(records) > 0:
        if last_date != records[-1][RECORD_DATE]:
            add_record(records, filtered_df.index[-1], last_row.close, TYPE_P, buy_count)
            print("################################# 最后一笔直接平仓")
    
    print(f"交易记录: {records}")
    # 总收益
    total_profit = sum(item[RECORD_PROFIT] for item in records)
    print_red(f"总收益：{total_profit}")
    #------------------------------------------ 图表显示 ---------------------------------------#
    if show_table:        
        SHEET_CLOSE = filtered_df.close.values
        SHEET_DATE = filtered_df.index
        # 设置字体，以支持中文显示
        # plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
        # plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
        # 创建图形和子图， ******** 一张图
        plt.figure(figsize=(15, 8))
        # 绘制股票涨跌幅
        plt.plot(SHEET_DATE, SHEET_CLOSE, marker='o', linestyle='-', color='b', label='CLOSE')
        # 折线图中显示自定义多、空条件
        for i in range(len(con_mets)):
            print(f"condition={i}, {con_mets[i]}")
            con_date = con_mets[i][CONDITION_DATE]
            sheet_index = SHEET_DATE.get_loc(con_date)
            print(f"sheet_index={sheet_index}")
            plt.annotate(f"{con_date.date()}({con_mets[i][CONDITION_MSG]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontsize=8)
        # 折线图中显示每次交易记录
        for i in range(len(records)):
            print(f"record={i}, {records[i]}")
            rec_date = records[i][RECORD_DATE]
            sheet_index = SHEET_DATE.get_loc(rec_date)
            print(f"sheet_index={sheet_index}")
            plt.annotate(f"{rec_date.date()}({records[i][INVEST_TYPE]})({records[i][RECORD_PROFIT]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,20), ha='center', color='red', fontsize=10)
        # 添加标题和标签
        plt.title("ZGPA", fontsize=14)
        init_info = f"Profit: {total_profit} ({start_date} ~ {end_date})(Count:{len(filtered_df)})"
        plt.xlabel(init_info, fontsize=14)
        plt.ylabel('Price', fontsize=14)
        # 显示图例
        plt.legend()
        # 显示网格
        plt.grid(True)
        # 显示图形
        plt.show()

if __name__ == "__main__":
    # 期货代码、起始日期、结束日期、交易手数、是否显示表格图形
    current_date = datetime.now().strftime("%Y-%m-%d")
    # result = simulated_invest(CODE_ZL, "2024-08-15", current_date, 1, TYPE_P, True)
    simulated_invest(STOCK_CODE, STOCK_START_DATE, STOCK_END_DATE, 1, True)