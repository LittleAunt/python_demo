# -*- coding: utf-8 -*-
# -------------------------- 根据纯碱主连的技术买卖点进行期权的买卖 --------------------------#
from CJZLSimulated import *
import pandas as pd

def print_red(p_str):
    print('\033[1;31;40m' + p_str + '\033[0m')

# 最大交易金额
MAX_AMOUNT = 5000

SA_DATA_PATH = "./gupiao/QIQDATA/SA/data/{}.txt"
KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
KEY_HY_CODE = "hy_code" # 合约代码前缀
KEY_HY_FILE = "hy_file" # 合约文件

QIQ_RECORD_DATE = "date" # 交易日期
QIQ_RECORD_HY_CODE = "code" # 交易合约代码
QIQ_RECORD_PRICE = "price" # 交易价格
QIQ_RECORD_AMOUNT = "amount" # 交易金额
QIQ_RECORD_COUNT = "count" # 交易数量
QIQ_RECORD_TYPE = "type" # 交易类型，买、卖
QIQ_RECORD_PROFIT = "profit" # 收益

QIQ_TYPE_S = 0
QIQ_TYPE_B = 1

CJZL_LIST = [
    # {KEY_START_DATE: "2023-10-20", KEY_END_DATE: "2023-12-04", KEY_HY_CODE: "SA401"},
    # {KEY_START_DATE: "2023-12-05", KEY_END_DATE: "2024-03-22", KEY_HY_CODE: "SA405"},
    {KEY_START_DATE: "2024-03-25", KEY_END_DATE: "2024-08-13", KEY_HY_CODE: "SA409"}
    #  {KEY_START_DATE: "2024-08-15", KEY_END_DATE: "2024-10-15", KEY_HY_CODE: "SA501"}
]

def simulated_all():
    result_list = []
    start_index = 0
    for i in range(start_index, len(CJZL_LIST)):
        result = simulated_invest(CODE_ZL, CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, TYPE_P, False)
        result_list.append(result)
    return result_list
        
def simulated_qiq(qh_records, code):
    qiq_d_record = [] # 买多记录
    qiq_k_record = [] # 买空记录
    file = SA_DATA_PATH.format(code)
    print(file)
    # 读取文件，指定分隔符为 '|'，并设置第一行为列名
    df = pd.read_csv(file, sep='|', skipinitialspace=True)
    # 去掉列名中的空格
    df.columns = df.columns.str.strip()
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    # df.date = pd.to_datetime(df.date)
    
    # filtered_df = df[df['date'] == "2024-09-18"]
    # # 再过滤对应的认购、认沽合约数据
    # filtered_df_d = filtered_df[filtered_df['code'].str.startswith("{}C".format(code))]
    # filtered_df_k = filtered_df[filtered_df['code'].str.startswith("{}P".format(code))] 
    # print(f"认购合约\n{filtered_df_d}")
    # print(f"认沽合约\n{filtered_df_k}")
    
    # 遍历期货每个交易点，进行期权交易
    for i in range(0, len(qh_records)):
        record = qh_records[i]
        r_date = record[RECORD_DATE].strftime('%Y-%m-%d')
        print(f"************* 交易日期：{r_date}")
        # 过滤出对应的日期数据
        filtered_df = df[df['date'] == r_date]
        # 再过滤对应的认购、认沽合约数据
        filtered_df_d = filtered_df[filtered_df['code'].str.startswith("{}C".format(code))]
        filtered_df_k = filtered_df[filtered_df['code'].str.startswith("{}P".format(code))]
        # *************** 认购合约找最高标的的，也就是最后一条数据交易
        # 1. 如果之前有买的记录，先卖掉上一笔认购
        if len(qiq_d_record) > 0:
            qiq_last_record = qiq_d_record[-1]
            if qiq_last_record[QIQ_RECORD_TYPE] == QIQ_TYPE_B:
                # 先找到对应的合约
                target_data = filtered_df_d.loc[filtered_df_d['code'] == qiq_last_record[QIQ_RECORD_HY_CODE]] 
                print(f"认购 卖 -----> 当前合约数据：\n{target_data}")
                # 再进行卖出交易
                if len(target_data) == 1:
                    s_amount = qiq_last_record[QIQ_RECORD_COUNT] * target_data.iloc[0].close * 20
                    profit = s_amount - qiq_last_record[QIQ_RECORD_AMOUNT]
                    t_record = {QIQ_RECORD_DATE: r_date, QIQ_RECORD_HY_CODE: qiq_last_record[QIQ_RECORD_HY_CODE], QIQ_RECORD_PRICE: target_data.iloc[0].close, QIQ_RECORD_AMOUNT: s_amount, QIQ_RECORD_COUNT: qiq_last_record[QIQ_RECORD_COUNT], QIQ_RECORD_TYPE: QIQ_TYPE_S, QIQ_RECORD_PROFIT: profit}
                    print(f"认购 卖 -----> 交易记录：\n{t_record}")
                    qiq_d_record.append(t_record)
                else:
                    print_red(" ################# 异常，未找到合约进行卖出 ################# ")
        # 2. 买入一笔认购, 如果是最后一笔交易，不买入
        if i < len(qh_records) - 1:
            last_data = filtered_df_d.iloc[-1]
            one_amount = last_data.close * 20
            count = (int)(MAX_AMOUNT / one_amount)
            b_amount = count * one_amount
            t_record = {QIQ_RECORD_DATE: r_date, QIQ_RECORD_HY_CODE: last_data.code, QIQ_RECORD_PRICE: last_data.close, QIQ_RECORD_AMOUNT: b_amount, QIQ_RECORD_COUNT: count, QIQ_RECORD_TYPE: QIQ_TYPE_B, QIQ_RECORD_PROFIT: 0}
            print(f"认购 买 -----> 交易记录：\n{t_record}")
            qiq_d_record.append(t_record)
        # *************** 认沽合约找最低标的的，也就是第一条数据交易
        # 1. 如果之前有买的记录，先卖掉上一笔认沽
        if len(qiq_k_record) > 0:
            qiq_last_record = qiq_k_record[-1]
            if qiq_last_record[QIQ_RECORD_TYPE] == QIQ_TYPE_B:
                # 先找到对应的合约
                target_data = filtered_df_k.loc[filtered_df_k['code'] == qiq_last_record[QIQ_RECORD_HY_CODE]] 
                print(f"认沽 卖 +++++> 当前合约数据：\n{target_data}")
                # 再进行卖出交易
                if len(target_data) == 1:
                    s_amount = qiq_last_record[QIQ_RECORD_COUNT] * target_data.iloc[0].close * 20
                    profit = s_amount - qiq_last_record[QIQ_RECORD_AMOUNT]
                    t_record = {QIQ_RECORD_DATE: r_date, QIQ_RECORD_HY_CODE: qiq_last_record[QIQ_RECORD_HY_CODE], QIQ_RECORD_PRICE: target_data.iloc[0].close, QIQ_RECORD_AMOUNT: s_amount, QIQ_RECORD_COUNT: qiq_last_record[QIQ_RECORD_COUNT], QIQ_RECORD_TYPE: QIQ_TYPE_S, QIQ_RECORD_PROFIT: profit}
                    print(f"认沽 卖 +++++> 交易记录：\n{t_record}")
                    qiq_k_record.append(t_record)
                else:
                    print_red(" ################# 异常，未找到合约进行卖出 ################# ")
        # 2. 买入一笔认沽, 如果是最后一笔交易，不买入
        if i < len(qh_records) - 1:
            first_data = filtered_df_k.iloc[0]
            one_amount = first_data.close * 20
            count = (int)(MAX_AMOUNT / one_amount)
            b_amount = count * one_amount
            t_record = {QIQ_RECORD_DATE: r_date, QIQ_RECORD_HY_CODE: first_data.code, QIQ_RECORD_PRICE: first_data.close, QIQ_RECORD_AMOUNT: b_amount, QIQ_RECORD_COUNT: count, QIQ_RECORD_TYPE: QIQ_TYPE_B, QIQ_RECORD_PROFIT: 0}
            print(f"认沽 买 +++++> 交易记录：\n{t_record}")
            qiq_k_record.append(t_record)
    # 计算总的认购和认沽收益
    d_total_profit = sum(item[QIQ_RECORD_PROFIT] for item in qiq_d_record)
    k_total_profit = sum(item[QIQ_RECORD_PROFIT] for item in qiq_k_record)
    total_profit = d_total_profit + k_total_profit
    print(f"#### 总认购收益：{d_total_profit}")
    print(f"#### 总认沽收益：{k_total_profit}")
    print(f"#### 总收益：{total_profit}")
        
if __name__ == "__main__":
    # 根据纯碱主联的走势找出每个买卖点
    result_list = simulated_all()
    
    for i in range(0, len(CJZL_LIST)):
        qh_records = result_list[i][RESULT_RECORDS]
        cjzl = CJZL_LIST[i]
        code = cjzl[KEY_HY_CODE]
        simulated_qiq(qh_records, code)
    
    # simulated_qiq(None, "SA501")