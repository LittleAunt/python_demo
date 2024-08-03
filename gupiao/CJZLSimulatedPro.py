# -*- coding: utf-8 -*-
# -------------------------- 模拟整个纯碱主连的交易，用每个合约的 K 线数据 --------------------------#
from CJOneSimulated import *

CODE_ZL = "233773"
CODE_01 = "233774"
CODE_05 = "233778"
CODE_09 = "233782"

KEY_CODE = "code"
KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
# 所有的主连对应的时间段
CJZL_LIST = [
    {KEY_CODE: CODE_05, KEY_START_DATE: "2019-12-18", KEY_END_DATE: "2020-04-20"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2020-04-20", KEY_END_DATE: "2020-08-20"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2020-08-20", KEY_END_DATE: "2020-12-21"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2020-12-21", KEY_END_DATE: "2021-04-24"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2021-04-24", KEY_END_DATE: "2021-08-15"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2021-08-15", KEY_END_DATE: "2021-12-17"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2021-12-17", KEY_END_DATE: "2022-04-13"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2022-04-13", KEY_END_DATE: "2022-08-19"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2022-08-19", KEY_END_DATE: "2022-12-20"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2022-12-20", KEY_END_DATE: "2023-04-12"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2023-04-12", KEY_END_DATE: "2023-08-19"}, # 09
    {KEY_CODE: CODE_01, KEY_START_DATE: "2023-08-19", KEY_END_DATE: "2023-12-22"}, # 01
    {KEY_CODE: CODE_05, KEY_START_DATE: "2023-12-22", KEY_END_DATE: "2024-04-10"}, # 05
    {KEY_CODE: CODE_09, KEY_START_DATE: "2024-04-10", KEY_END_DATE: "2024-08-03"}  # 09
]

def simulated_all(show_table):
    result_list = []
    for i in range(0, len(CJZL_LIST)):
        result = simulated_invest(CJZL_LIST[i][KEY_CODE], CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, False)
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