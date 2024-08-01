# -*- coding: utf-8 -*-
# -------------------------- 模拟整个纯碱主连的交易 --------------------------#
from MyQHDemo import *

KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
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
    {KEY_START_DATE: "2024-03-25", KEY_END_DATE: "2024-07-31"}
]

def simulated_all(show_table):
    result_list = []
    start_index = 0
    for i in range(start_index, len(CJZL_LIST)):
        if i == start_index:
            result = simulated_invest("233773", CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, TYPE_P, False)
        else:
            result = simulated_invest("233773", CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, result_list[-1][RESULT_NEXT_TYPE], False)
        result_list.append(result)
    print(result_list)
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
        init_info = f"Count: {len(result_list)}, Total Profit: {total_profit}"
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