# -*- coding: utf-8 -*-
# -------------------------- 模拟整个纯碱主连的交易，用的是主连的 K 线数据 --------------------------#
from CJZLSimulated import *

CODE_ZL = "233773"
CODE_01 = "233774"
CODE_05 = "233778"
CODE_09 = "233782"

KEY_CODE = "code"
KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
KEY_MAX_DATE = "max_date"
# 所有的主连对应的时间段
CJZL_LIST = [
    {KEY_START_DATE: "2019-12-18", KEY_END_DATE: "2020-04-16"},
    {KEY_START_DATE: "2020-04-17", KEY_END_DATE: "2020-08-18"},
    {KEY_START_DATE: "2020-08-19", KEY_END_DATE: "2020-12-17"},
    {KEY_START_DATE: "2020-12-18", KEY_END_DATE: "2021-04-08"},
    {KEY_START_DATE: "2021-04-09", KEY_END_DATE: "2021-07-28"},
    {KEY_START_DATE: "2021-07-29", KEY_END_DATE: "2021-12-01"},
    {KEY_START_DATE: "2021-12-02", KEY_END_DATE: "2022-03-24"},
    {KEY_START_DATE: "2022-03-25", KEY_END_DATE: "2022-08-03"},
    {KEY_START_DATE: "2022-08-04", KEY_END_DATE: "2022-12-01"},
    {KEY_START_DATE: "2022-12-02", KEY_END_DATE: "2023-03-23"},
    {KEY_START_DATE: "2023-03-24", KEY_END_DATE: "2023-08-02"},
    {KEY_START_DATE: "2023-08-03", KEY_END_DATE: "2023-12-04"},
    {KEY_START_DATE: "2023-12-05", KEY_END_DATE: "2024-03-22"},
    {KEY_START_DATE: "2024-03-25", KEY_END_DATE: "2024-08-14"}
]

def simulated_all(show_table):
    result_list = []
    # start_index = len(CJZL_LIST) - 3
    start_index = 0
    for i in range(start_index, len(CJZL_LIST)):
        result = simulated_invest(CODE_ZL, CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, TYPE_P, False)
        # if i == start_index:
        #     result = simulated_invest("233773", CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, TYPE_P, False)
        # else:
        #     result = simulated_invest("233773", CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, result_list[-1][RESULT_NEXT_TYPE], False)
        result_list.append(result)
    # print(result_list)
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
        plt.title("CJZL", fontsize=14)
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