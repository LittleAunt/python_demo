# -*- coding: utf-8 -*-

from  QHRequest import *
from  MyTT import * 
from MyQHCondition import *
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 每笔投资记录
RECORD_DATE = "record_date" # 交易日期
RECORD_PRICE = "record_price" # 交易价格
RECORD_TYPE = "record_type" # 0,1,2 分别代表做多、做空、平仓
TYPE_D = 0
TYPE_K = 1
TYPE_P = 2
RECORD_PROFIT = "record_profit" # 收益
# 满足各种买卖条件的记录
CON_MET_DATE = "con_met_date"
CON_MET_MSG = "con_met_msg"
# 模拟结果字段
RESULT_PROFIT = "result_profit"
RESULT_START_DATE = "result_start_date"
RESULT_END_DATE = "result_end_date"
RESULT_NEXT_TYPE = "result_next_type" # 下一个主连开始应该做多、空、平

# 计算收益。根据 duo 判断是做多还是空
def cal_profit(last_price, cur_price, buy_count, duo):
    last_amount = last_price * buy_count * 20
    change = (cur_price - last_price) / last_price
    if duo:
        return round(last_amount * change, 2)
    else:
        return round(-1 * last_amount * change, 2)

# 添加一条交易记录
def add_record(records, date, price, type, buy_count):
    # 列表为空，直接插入一条交易记录
    if len(records) == 0:
        records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: 0})
    else: # 取最后一次交易记录，与当前交易进行对比计算收益
        last_record = records[-1]
        # 1. 当前是做多
        if type == TYPE_D:
            if last_record[RECORD_TYPE] == TYPE_K: # 之前是做空，计算收益
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, False)})
            elif last_record[RECORD_TYPE] == TYPE_P: # 之前是平仓，直接插入一条新交易
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: 0})
        # 2. 当前是做空
        elif type == TYPE_K:
            if last_record[RECORD_TYPE] == TYPE_D: # 之前是做多，计算收益
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, True)})
            elif last_record[RECORD_TYPE] == TYPE_P: # 之前是平仓，直接插入一条新交易
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: 0})
        # 3. 当前是做平,无论是做多还是做空都开始计算收益
        elif type == TYPE_P:
            if last_record[RECORD_TYPE] == TYPE_D:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, True)})
            elif last_record[RECORD_TYPE] == TYPE_K:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, RECORD_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, False)})

# 模拟交易，计算收益
def simulated_invest(code, sd, ed, buy_count, show_table):
    records = [] # 交易记录列表
    con_mets = [] # 满足各种自定义条件的列表
    start_date = pd.to_datetime(sd) # 将字符串日期转换为 datetime 类型
    end_date = pd.to_datetime(ed)
    days_before = 200 # 起始天数往前多取 120 天，用于计算 MACD 指标
    date_before = start_date - timedelta(days=days_before)
    df = get_price_day(code, date_before.strftime('%Y-%m-%d'), ed)
    OPEN = df.open.values # 开盘列表
    CLOSE = df.close.values # 收盘列表
    # 过滤想要的日期时间段数据
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df[mask]
    # MACD 三项指标
    M_DIFF, M_DEA, M_MACD = MACD(df.close.values)
    # 遍历表格，计算收益
    for i in range(3, len(df)):  # 最多取前三天的数据对比，所以从 3 开始
        if (df.index[i] < start_date):
            continue
        cur_row = df.iloc[i] # 当天
        cur_date = df.index[i]
        
        # 1. MACD 金叉、死叉
        if MACD_JC(M_DIFF, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "JC"}) # 金叉
            add_record(records, cur_date, cur_row.close, TYPE_D, buy_count)
        if MACD_SC(M_DIFF, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "SC"}) # 死叉
            add_record(records, cur_date, cur_row.close, TYPE_K, buy_count)
        # 2. MACD 溢出
        if MACD_UP_YC(M_MACD, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "PD"}) # 平多
            add_record(records, cur_date, cur_row.close, TYPE_P, buy_count)
        if MACD_DOWN_YC(M_MACD, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "PK"}) # 平空
            add_record(records, cur_date, cur_row.close, TYPE_P, buy_count)
        # 3. 三连红、三连绿
        if RED_K3(OPEN, CLOSE, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "3D"}) # 三多
            add_record(records, cur_date, cur_row.close, TYPE_D, buy_count)
        if GREEN_K3(OPEN, CLOSE, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "3K"}) # 三空
            add_record(records, cur_date, cur_row.close, TYPE_K, buy_count)
        # 4. 反转做多、做空。三连绿后，MACD线比前一天高               (需设定范围，高 0.1 也是高)
        if MACD_UP_AFTER_GREEN_K3(OPEN, CLOSE, M_MACD, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZD0"}) # 转多0
            add_record(records, cur_date, cur_row.close, TYPE_D, buy_count)
        if MACD_DOWN_AFTER_RED_K3(OPEN, CLOSE, M_MACD, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZK0"}) # 转空0
            add_record(records, cur_date, cur_row.close, TYPE_K, buy_count)
        # 5. 反转做多、做空。MACD首次大于前一天，MACD未溢出           (需设定范围，高 0.1 也是高)
        if MACD_UP_V(M_MACD, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZD1"}) # 转多1
            add_record(records, cur_date, cur_row.close, TYPE_D, buy_count)
        if MACD_DOWN_V(M_MACD, M_DEA, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZK1"}) # 转空1
            add_record(records, cur_date, cur_row.close, TYPE_K, buy_count)
        # 6. 触碰反转做多，做空。MACD 呈 V 字型，中间值小于 12。相当于 DIFF DEA 差点碰到一起。 (需设定范围，高 0.1 也是高)
        if MACD_UP_V_CP(M_MACD, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "CD"}) # 触多
            add_record(records, cur_date, cur_row.close, TYPE_D, buy_count)
        if MACD_DOWN_V_CP(M_MACD, i):
            con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "CK"}) # 触空
            add_record(records, cur_date, cur_row.close, TYPE_K, buy_count)
    
    # 取最后一笔交易如果没平仓，直接平仓，并设置下一个主连开始时应该执行的操作
    result_next_type = TYPE_P
    last_date = df.index[-1]
    last_row = df.iloc[-1]
    if len(records) > 0:
        if last_date != records[-1][RECORD_DATE]:
            add_record(records, df.index[-1], last_row.close, TYPE_P, buy_count)
            print("################################# 最后一笔直接平仓")
            if len(records) >= 2:
                second_last_record = records[-2]
                result_next_type = second_last_record[RECORD_TYPE]
        else:
            result_next_type = records[-1][RECORD_TYPE]
        
    # 总收益
    total_profit = sum(item[RECORD_PROFIT] for item in records)
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
            con_date = con_mets[i][CON_MET_DATE]
            sheet_index = SHEET_DATE.get_loc(con_date)
            print(f"sheet_index={sheet_index}")
            plt.annotate(f"{con_date.date()}({con_mets[i][CON_MET_MSG]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontsize=8)
        # 折线图中显示每次交易记录
        for i in range(len(records)):
            print(f"record={i}, {records[i]}")
            rec_date = records[i][RECORD_DATE]
            sheet_index = SHEET_DATE.get_loc(rec_date)
            print(f"sheet_index={sheet_index}")
            plt.annotate(f"{rec_date.date()}({records[i][RECORD_TYPE]})({records[i][RECORD_PROFIT]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,20), ha='center', color='red', fontsize=8)
        # 添加标题和标签
        plt.title("CJZL", fontsize=14)
        init_info = f"Profit: {total_profit} ({start_date} ~ {end_date})(Count:{len(filtered_df)})"
        plt.xlabel(init_info, fontsize=14)
        plt.ylabel('Price', fontsize=14)
        # 显示图例
        plt.legend()
        # 显示网格
        plt.grid(True)
        # 显示图形
        plt.show()
    # 返回总收益
    return {RESULT_PROFIT: total_profit, RESULT_START_DATE: sd, RESULT_END_DATE: ed, RESULT_NEXT_TYPE: result_next_type}

if __name__ == "__main__":
    # 期货代码、起始日期、结束日期、交易手数、是否显示表格图形
    result = simulated_invest("233773", "2023-12-11", "2024-03-22", 1, True)
    print(f"result: {result}")