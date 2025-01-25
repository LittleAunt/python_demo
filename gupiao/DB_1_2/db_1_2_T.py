# -*- coding:utf-8 -*-
# 打板一进二。二板开盘一字，然后开板，5个点处买入，看第二日收益情况
import sys
import os
# 获取脚本文件所在目录的父目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的绝对路径
parent_dir = os.path.dirname(current_dir)  # 获取父目录路径
# 将父目录路径添加到 sys.path 中
sys.path.append(parent_dir)

from Ashare import *
import datetime
import calendar
import time

# 买入预设的百分比
BUY_PERCENT = 1.05
# 开盘预设的百分比
OPEN_PERCENT = 1.09
# 结束日期
E_DATE = "2025-01-22"
# 分析天数
D_COUNT = 365
# 首板前两日涨幅，最大要求
MAX_ZF_2 = 30

# 是否收盘涨停
def isCloseZT(d1, d2):
    zt_price = round(d1.close * 1.1, 2)
    if d2.close == zt_price:
        return True
    else:
        return False

# 是否开盘涨停
def isOpenZT(d1, d2):
    zt_price = round(d1.close * OPEN_PERCENT, 2)
    if d2.open >= zt_price:
        return True
    else:
        return False
    
# 打板1进2，交易记录和收益
def db_1_2(code):
    result = []
    df=get_price(code,frequency='1d',count=D_COUNT, end_date=E_DATE, tx_channel=False)
    # print(df)
    had_buy = False
    buy_record = {}
    for i in range(4, len(df)):
        # 1. 先判断是否需要卖出
        if had_buy:
            # 涨停跳过，继续看下一日
            if isCloseZT(df.iloc[i - 1], df.iloc[i]) and i != len(df) - 1: # 不是最后一天
                continue
            # 未涨停，直接收盘价卖出，计算收益
            else:
                had_buy = False
                cur_data = df.iloc[i]
                buy_record["s_date"] = df.index[i].date()
                buy_record["s_price"] = cur_data.close
                buy_record["profit"] = round((cur_data.close - buy_record["b_price"]) / buy_record["b_price"] * 100, 2)
                result.append(buy_record)
                continue
        
        # 2. 再寻找买点
        data0 = df.iloc[i - 4]
        # data1, data2 前两日未涨停,且总涨幅不大于 11， 然后第三日涨停 data3，也就是首版
        data1 = df.iloc[i - 3]
        data2 = df.iloc[i - 2]
        data3 = df.iloc[i - 1]
        d1_zf = round((data1.close - data0.close) / data0.close * 100, 2)
        d2_zf = round((data2.close - data1.close) / data1.close * 100, 2)
        zf_2 = d1_zf + d2_zf
        if isCloseZT(data0, data1) or isCloseZT(data1, data2): #or zf_2 > MAX_ZF_2:
            continue
        if not isCloseZT(data2, data3):
            continue
        # 跳过 2024-10-08日
        skip_date = datetime.datetime.strptime("2024-10-08", "%Y-%m-%d")
        if df.index[i] == skip_date:
            continue
        # 第二日是否开盘一字板,且走出T字
        data4 = df.iloc[i]
        if isOpenZT(data3, data4) and data4.open == data4.close and data4.low < data4.open:
            had_buy = True
            buy_record = {}
            buy_record["b_date"] = df.index[i].date()
            buy_record["b_price"] = data4.open
                
    
    return result

def printResult(code, total_profit, result): 
    print(f"############# 股票代码: {code}, 总收益: {total_profit}")
    for r in result:
        print(r)
        
def getYLCount(result):
    count = 0
    for r in result:
        if r["profit"] >= 0:
            count += 1
    return count

def getKSCount(result):
    count = 0
    for r in result:
        if r["profit"] < 0:
            count += 1
    return count


# 上证
def runSH():
    sh_profit_list = []
    sh_profit_yl_count = 0 # 正收益次数
    sh_profit_ks_count = 0 # 负收益次数

    sh_code_prefix = 600000
    sh_start_code = 0
    sh_end_code = 5600
    # sh_end_code = 15
    for code in range(sh_start_code, sh_end_code):
        # 上证没有 4000 开头的，所以跳过
        highest_digit = code // 1000  # 提取最高位
        if highest_digit == 4:
            continue
        sh_code = f"sh{sh_code_prefix + code}"
        # print(f"开始分析股票: {sh_code}")
        result = db_1_2(sh_code)
        # 打印结果
        if len(result) != 0:
            total_profit = round(sum(item["profit"] for item in result), 2)
            printResult(sh_code, total_profit, result)
            sh_profit_list.append(total_profit)
            sh_profit_yl_count += getYLCount(result)
            sh_profit_ks_count += getKSCount(result)
            
        time.sleep(1) 
        
    sh_total_profit = sum(item for item in sh_profit_list)
    print(f"**********************  上证总收益: {sh_total_profit}, 总次数: {sh_profit_yl_count + sh_profit_ks_count}, 盈利次数: {sh_profit_yl_count}, 亏损次数: {sh_profit_ks_count}")
  
# 深证
def runSZ():
    sh_profit_list = []
    sh_profit_yl_count = 0 # 正收益次数
    sh_profit_ks_count = 0 # 负收益次数

    sh_start_code = 1
    sh_end_code = 3816
    # sh_end_code = 5
    for code in range(sh_start_code, sh_end_code):
        sh_code = f"sz{str(code).zfill(6)}"
        # print(f"开始分析股票: {sh_code}")
        result = db_1_2(sh_code)
        # 打印结果
        if len(result) != 0:
            total_profit = round(sum(item["profit"] for item in result), 2)
            printResult(sh_code, total_profit, result)
            sh_profit_list.append(total_profit)
            sh_profit_yl_count += getYLCount(result)
            sh_profit_ks_count += getKSCount(result)
            
        time.sleep(1.5) 
        
    sh_total_profit = sum(item for item in sh_profit_list)
    print(f"**********************  深证总收益: {sh_total_profit}, 总次数: {sh_profit_yl_count + sh_profit_ks_count}, 盈利次数: {sh_profit_yl_count}, 亏损次数: {sh_profit_ks_count}")
     
if __name__ == "__main__":
    # runSH()
    runSZ()