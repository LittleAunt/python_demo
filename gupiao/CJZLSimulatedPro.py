# -*- coding: utf-8 -*-
# -------------------------- 模拟一个主连的交易 --------------------------#
from  QHRequest import *
from  MyTT import * 
from MyQHCondition import *
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 交易类型。0,1,2 分别代表做多、做空、平仓
INVEST_TYPE = "invest_type" 
TYPE_D = 0
TYPE_K = 1
TYPE_P = 2
# 每笔投资记录
RECORD_DATE = "record_date" # 交易日期
RECORD_PRICE = "record_price" # 交易价格
RECORD_PROFIT = "record_profit" # 收益
# 满足各种买卖条件的记录
CON_MET_DATE = "con_met_date"
CON_MET_MSG = "con_met_msg"
# 模拟结果字段
RESULT_PROFIT = "result_profit"
RESULT_START_DATE = "result_start_date"
RESULT_END_DATE = "result_end_date"
RESULT_RECORDS = "result_records"

# 计算收益。根据 duo 判断是做多还是空
def cal_profit(last_price, cur_price, buy_count, duo):
    last_amount = last_price * buy_count * 20
    change = (cur_price - last_price) / last_price
    if duo:
        return round(last_amount * change, 2)
    else:
        return round(-1 * last_amount * change, 2)

# 条件判断，是否满足自定义指标要求
def condition_matched(con_mets, cur_date, M_DIFF, M_DEA, M_MACD, OPEN, CLOSE, i):
    matched = False
    # 1. MACD 金叉、死叉
    if MACD_JC(M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "JC", INVEST_TYPE: TYPE_D}) # 金叉
        matched = True
    if MACD_SC(M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "SC", INVEST_TYPE: TYPE_K}) # 死叉
        matched = True
    # 2. MACD 溢出
    if MACD_UP_YC(M_MACD, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "PD", INVEST_TYPE: TYPE_P}) # 平多
        matched = True
    if MACD_DOWN_YC(M_MACD, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "PK", INVEST_TYPE: TYPE_P}) # 平空
        matched = True
    # 3. 三连红、三连绿
    # if RED_K3(OPEN, CLOSE, i):
    #     con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "3D", INVEST_TYPE: TYPE_D}) # 三多
    #     matched = True
    # if GREEN_K3(OPEN, CLOSE, i):
    #     con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "3K", INVEST_TYPE: TYPE_K}) # 三空
    #     matched = True
    # # 4. 反转做多、做空。三连绿后，MACD线比前一天高               (需设定范围，高 0.1 也是高)
    # if MACD_UP_AFTER_GREEN_K3(OPEN, CLOSE, M_MACD, i):
    #     con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZD0", INVEST_TYPE: TYPE_D}) # 转多0
    #     matched = True
    # if MACD_DOWN_AFTER_RED_K3(OPEN, CLOSE, M_MACD, i):
    #     con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZK0", INVEST_TYPE: TYPE_K}) # 转空0
    #     matched = True
    # 5. 反转做多、做空。MACD首次大于前一天，MACD未溢出           (需设定范围，高 0.1 也是高)
    if MACD_UP_V(M_MACD, M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZD1", INVEST_TYPE: TYPE_D}) # 转多1
        matched = True
    if MACD_DOWN_V(M_MACD, M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "ZK1", INVEST_TYPE: TYPE_K}) # 转空1
        matched = True
    # 6. 触碰反转做多，做空。MACD 呈 V 字型，中间值小于 12。相当于 DIFF DEA 差点碰到一起。 (需设定范围，高 0.1 也是高)
    if MACD_UP_V_CP(M_MACD, M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "CD", INVEST_TYPE: TYPE_D}) # 触多
        matched = True
    if MACD_DOWN_V_CP(M_MACD, M_DIFF, M_DEA, i):
        con_mets.append({CON_MET_DATE: cur_date, CON_MET_MSG: "CK", INVEST_TYPE: TYPE_K}) # 触空
        matched = True
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
            if last_record[INVEST_TYPE] == TYPE_K: # 之前是做空，计算收益
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, False)})
            elif last_record[INVEST_TYPE] == TYPE_P: # 之前是平仓，直接插入一条新交易
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: 0})
        # 2. 当前是做空
        elif type == TYPE_K:
            if last_record[INVEST_TYPE] == TYPE_D: # 之前是做多，计算收益
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, True)})
            elif last_record[INVEST_TYPE] == TYPE_P: # 之前是平仓，直接插入一条新交易
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: 0})
        # 3. 当前是做平,无论是做多还是做空都开始计算收益
        elif type == TYPE_P:
            if last_record[INVEST_TYPE] == TYPE_D:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, True)})
            elif last_record[INVEST_TYPE] == TYPE_K:
                records.append({RECORD_DATE: date, RECORD_PRICE: price, INVEST_TYPE: type, RECORD_PROFIT: cal_profit(last_record[RECORD_PRICE], price, buy_count, False)})

# 模拟交易，计算收益. forced_liquidation 最后一个交易日是否强制平仓
def simulated_invest(code, sd, ed, buy_count, first_type, show_table, forced_liquidation):
    print(f"开始日期：{sd}，结束日期：{ed}")
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
    for i in range(0, len(df)):
        cur_row = df.iloc[i]
        cur_date = df.index[i]
            
        # 匹配买卖点
        matched = condition_matched(con_mets, cur_date, M_DIFF, M_DEA, M_MACD, OPEN, CLOSE, i) 
        # 第一天特殊处理，用上一个主连确定的类型买入
        if df.index[i] == start_date:
            if first_type != TYPE_P: # 不是平仓，买入
                add_record(records, cur_date, cur_row.close, first_type, buy_count)
        elif df.index[i] > start_date:
            if matched: # 匹配到对应的买卖点，添加一条记录
                add_record(records, cur_date, cur_row.close, con_mets[-1][INVEST_TYPE], buy_count)
                
    # 取最后一笔交易如果没平仓，直接平仓，并设置下一个主连开始时应该执行的操作
    if forced_liquidation:
        last_date = df.index[-1]
        last_row = df.iloc[-1]
        if len(records) > 0:
            if last_date != records[-1][RECORD_DATE]:
                add_record(records, df.index[-1], last_row.close, TYPE_P, buy_count)
                print("################################# 最后一笔直接平仓")
                
    # print(f"{code}: ###### 交易记录: {records}")
    # 总收益
    total_profit = sum(item[RECORD_PROFIT] for item in records)
    print(f"总收益：{total_profit}")
    #------------------------------------------ 图表显示 ---------------------------------------#
    if show_table:        
        SHEET_CLOSE = filtered_df.close.values
        SHEET_DATE = filtered_df.index
        # 过滤设置的时间段的匹配买卖点
        # 转换为 DataFrame
        con_mets_df = pd.DataFrame(con_mets)
        # df.set_index([CON_MET_DATE], inplace=True)
        # 过滤数据
        cm_filtered_df = con_mets_df[(con_mets_df[CON_MET_DATE] >= start_date) & (con_mets_df[CON_MET_DATE] <= end_date)]
        print(cm_filtered_df)
        # 创建图形和子图， ******** 一张图
        plt.figure(figsize=(15, 8))
        # 绘制股票涨跌幅
        plt.plot(SHEET_DATE, SHEET_CLOSE, marker='o', linestyle='-', color='b', label='CLOSE')
        # 折线图中显示自定义多、空条件
        for i in range(len(cm_filtered_df)):
            con_date = cm_filtered_df.iloc[i][CON_MET_DATE]
            sheet_index = SHEET_DATE.get_loc(con_date)
            plt.annotate(f"{con_date.date()}({cm_filtered_df.iloc[i][CON_MET_MSG]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontsize=8)
        # 折线图中显示每次交易记录
        for i in range(len(records)):
            print(f"record={i}, {records[i]}")
            rec_date = records[i][RECORD_DATE]
            sheet_index = SHEET_DATE.get_loc(rec_date)
            plt.annotate(f"{rec_date.date()}({records[i][INVEST_TYPE]})({records[i][RECORD_PROFIT]})", (SHEET_DATE[sheet_index], SHEET_CLOSE[sheet_index]), textcoords="offset points", xytext=(0,20), ha='center', color='red', fontsize=12)
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
    return {RESULT_PROFIT: total_profit, RESULT_START_DATE: sd, RESULT_END_DATE: ed, RESULT_RECORDS: records}

if __name__ == "__main__":
    # 期货代码、起始日期、结束日期、交易手数、是否显示表格图形
    result = simulated_invest("233773", "2024-03-25", "2024-07-31", 1, TYPE_P, True, True)
    print(f"result: {result}")