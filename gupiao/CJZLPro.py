# -*- coding: utf-8 -*-
# -------------------------- 模拟整个纯碱主连的交易，每次主连切换后用前面子连的K线决定第一次买卖 --------------------------#
from CJZLSimulatedPro import *

CODE_ZL = "233773"
CODE_01 = "233774"
CODE_05 = "233778"
CODE_09 = "233782"

KEY_CODE = "code"
KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
KEY_MIN_DATE = "min_date" # 主连结束后第一天
KEY_MAX_DATE = "max_date" # 主连结束后到合约交割最后一天
# 所有的主连对应的时间段
CJZL_LIST = [
    {KEY_CODE: CODE_05, KEY_START_DATE: "2019-12-18", KEY_END_DATE: "2020-04-16", KEY_MIN_DATE: "2020-04-17",KEY_MAX_DATE: "2020-04-30"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2020-04-17", KEY_END_DATE: "2020-08-18", KEY_MIN_DATE: "2020-08-19",KEY_MAX_DATE: "2020-08-31"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2020-08-19", KEY_END_DATE: "2020-12-17", KEY_MIN_DATE: "2020-12-18",KEY_MAX_DATE: "2020-12-31"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2020-12-18", KEY_END_DATE: "2021-04-08", KEY_MIN_DATE: "2021-04-09",KEY_MAX_DATE: "2021-04-30"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2021-04-09", KEY_END_DATE: "2021-07-28", KEY_MIN_DATE: "2021-07-29",KEY_MAX_DATE: "2021-08-31"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2021-07-29", KEY_END_DATE: "2021-12-01", KEY_MIN_DATE: "2021-12-02",KEY_MAX_DATE: "2021-12-31"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2021-12-02", KEY_END_DATE: "2022-03-24", KEY_MIN_DATE: "2022-03-25",KEY_MAX_DATE: "2022-04-30"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2022-03-25", KEY_END_DATE: "2022-08-03", KEY_MIN_DATE: "2022-08-04",KEY_MAX_DATE: "2022-08-31"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2022-08-04", KEY_END_DATE: "2022-12-01", KEY_MIN_DATE: "2022-12-02",KEY_MAX_DATE: "2022-12-31"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2022-12-02", KEY_END_DATE: "2023-03-23", KEY_MIN_DATE: "2023-03-24",KEY_MAX_DATE: "2023-04-30"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2023-03-24", KEY_END_DATE: "2023-08-02", KEY_MIN_DATE: "2023-08-03",KEY_MAX_DATE: "2023-08-31"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2023-08-03", KEY_END_DATE: "2023-12-04", KEY_MIN_DATE: "2023-12-05",KEY_MAX_DATE: "2023-12-31"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2023-12-05", KEY_END_DATE: "2024-03-22", KEY_MIN_DATE: "2024-03-23",KEY_MAX_DATE: "2024-04-30"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2024-03-25", KEY_END_DATE: "2024-07-31", KEY_MIN_DATE: "2024-07-31",KEY_MAX_DATE: "2024-07-31"}  # 09
]

BUY_COUNT = 1

def simulated_all(show_table):
    result_list = []
    # start_index = len(CJZL_LIST) - 3
    start_index = 0
    for i in range(start_index, len(CJZL_LIST)):
        # 如果是第一次交易，直接用主连数据，上一次的交易类型相当于平仓
        if i == start_index:
            result = simulated_invest(CODE_ZL, CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], BUY_COUNT, TYPE_P, False, False)
            # print(f"######## result={result}")
        else:
            pre_host_result = result_list[-1]
            pre_host_records = pre_host_result[RESULT_RECORDS]
            pre_host_last_record = pre_host_records[-1]
            # 先用上一个子连跑一下结果，然后根据子连在切换主连之后的第一个买卖点决定下一个主连的开始时间和买卖类型
            pre_cjzl = CJZL_LIST[i - 1]
            pre_sub_result = simulated_invest(pre_cjzl[KEY_CODE], pre_cjzl[KEY_MIN_DATE], pre_cjzl[KEY_MAX_DATE], BUY_COUNT, TYPE_P, False, True)
            # print(f"上一个子连的尾部交易: {pre_sub_result}")
            # 找到上一个子连尾部的交易记录，找到第一个反向买点，用下一个主连进行操作
            pre_sub_result_records = pre_sub_result[RESULT_RECORDS]
            next_type = TYPE_P
            next_start_date = pre_cjzl[KEY_MAX_DATE]
            new_record = {}
            for j in range(0, len(pre_sub_result_records)):
                pre_sub_record = pre_sub_result_records[j]
                # 找到反向买卖，平仓上一个主连
                if pre_sub_record[INVEST_TYPE] == TYPE_D:
                    if pre_host_last_record[INVEST_TYPE] == TYPE_K:
                        new_profit = cal_profit(pre_host_last_record[RECORD_PRICE], pre_sub_record[RECORD_PRICE], BUY_COUNT, False)
                        new_record = {RECORD_DATE: pre_sub_record[RECORD_DATE], RECORD_PRICE: pre_sub_record[RECORD_PRICE], INVEST_TYPE: TYPE_D, RECORD_PROFIT: new_profit}
                        pre_host_records.append(new_record)
                if pre_sub_record[INVEST_TYPE] == TYPE_K:
                    if pre_host_last_record[INVEST_TYPE] == TYPE_D:
                        new_profit = cal_profit(pre_host_last_record[RECORD_PRICE], pre_sub_record[RECORD_PRICE], BUY_COUNT, True)
                        new_record = {RECORD_DATE: pre_sub_record[RECORD_DATE], RECORD_PRICE: pre_sub_record[RECORD_PRICE], INVEST_TYPE: TYPE_K, RECORD_PROFIT: new_profit}
                        pre_host_records.append(new_record)
                if pre_sub_record[INVEST_TYPE] == TYPE_P:
                    if pre_host_last_record[INVEST_TYPE] == TYPE_D:
                        new_profit = cal_profit(pre_host_last_record[RECORD_PRICE], pre_sub_record[RECORD_PRICE], BUY_COUNT, True)
                        new_record = {RECORD_DATE: pre_sub_record[RECORD_DATE], RECORD_PRICE: pre_sub_record[RECORD_PRICE], INVEST_TYPE: TYPE_P, RECORD_PROFIT: new_profit}
                        pre_host_records.append(new_record)
                    if pre_host_last_record[INVEST_TYPE] == TYPE_K:
                        new_profit = cal_profit(pre_host_last_record[RECORD_PRICE], pre_sub_record[RECORD_PRICE], BUY_COUNT, False)
                        new_record = {RECORD_DATE: pre_sub_record[RECORD_DATE], RECORD_PRICE: pre_sub_record[RECORD_PRICE], INVEST_TYPE: TYPE_P, RECORD_PROFIT: new_profit}
                        pre_host_records.append(new_record)
                if pre_sub_record[INVEST_TYPE] != pre_host_last_record[INVEST_TYPE]:
                    next_start_date = pre_sub_record[RECORD_DATE].strftime('%Y-%m-%d')
                    next_type = pre_sub_record[INVEST_TYPE]
                    break
            print(f"新增的交易记录： {new_record}")
            # 因为上一个主连最后通过子连进行平仓，需要重新计算一次收益
            total_profit = sum(item[RECORD_PROFIT] for item in pre_host_records)
            pre_host_result[RESULT_PROFIT] = total_profit
            print(f"新的收益结果：{total_profit}")
            # 开始下一个主连,如果是最后一个主连，最后的交易日要平仓
            if i == len(CJZL_LIST) - 1:
                forced_liquidation = True
            else:
                forced_liquidation = False
            result = simulated_invest(CODE_ZL, next_start_date, CJZL_LIST[i][KEY_END_DATE], BUY_COUNT, next_type, False, forced_liquidation)    
            # print(f"######## result={result}")            
        result_list.append(result)
        
    # 打印所有交易记录
    for i in range(0, len(result_list)):
        print(f"############# 收益： {result_list[i][RESULT_PROFIT]}")
        for j in range(0, len(result_list[i][RESULT_RECORDS])):
            print(result_list[i][RESULT_RECORDS][j])
    # 找出所有交易记录中最大和最小的两条记录
    max_record = max(result_list[0][RESULT_RECORDS], key=lambda x: x[RECORD_PROFIT])
    min_record = min(result_list[0][RESULT_RECORDS], key=lambda x: x[RECORD_PROFIT])
    for i in range(1, len(result_list)):
        max_temp_r = max(result_list[i][RESULT_RECORDS], key=lambda x: x[RECORD_PROFIT])
        max_record = max_record if max_record[RECORD_PROFIT] > max_temp_r[RECORD_PROFIT] else max_temp_r
        min_temp_r = min(result_list[i][RESULT_RECORDS], key=lambda x: x[RECORD_PROFIT])
        min_record = min_record if min_record[RECORD_PROFIT] < min_temp_r[RECORD_PROFIT] else min_temp_r
    print(f"最赚的一笔交易：{max_record}")
    print(f"最亏的一笔交易：{min_record}")
    # 总收益
    total_profit = sum(item[RESULT_PROFIT] for item in result_list)
    print(f"最终总收益: {total_profit}")
    if show_table:        
        SHEET_PROFIT = [item[RESULT_PROFIT] for item in result_list]
        SHEET_DATE = [item[RESULT_END_DATE] for item in result_list]
        # 创建图形和子图， ******** 一张图
        plt.figure(figsize=(15, 8))
        # 绘制股票涨跌幅
        plt.plot(SHEET_DATE, SHEET_PROFIT, marker='o', linestyle='-', color='b', label='PROFIT')
        # 折线图中显示自定义多、空条件
        for i in range(len(result_list)):
            plt.annotate(f"{SHEET_PROFIT[i]}", (SHEET_DATE[i], SHEET_PROFIT[i]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontsize=10)
        # 添加标题和标签
        plt.title("CJZLPro", fontsize=14)
        init_info = f"Count: {len(result_list)}, Total Profit: {total_profit}, Max: {max_record[RECORD_PROFIT]}({max_record[RECORD_DATE].date()}), Min: {min_record[RECORD_PROFIT]}({min_record[RECORD_DATE].date()})"
        plt.xlabel(init_info, fontsize=14)
        plt.ylabel('PROFIT', fontsize=14)
        # 显示图例
        plt.legend()
        # 显示网格
        plt.grid(True)
        # 显示图形
        plt.show()
if __name__ == "__main__":
    simulated_all(True)