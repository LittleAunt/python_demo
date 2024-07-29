from  Ashare import *
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext

# 设置精度
getcontext().prec = 28

MIN_CHANGE = Decimal('1.0') # 每次交易依据的最小涨跌幅度
MAX_CHANGE = Decimal('2.0') # 每次交易依据的最大涨跌幅度
CHANGE_STEP = Decimal('0.1') # 每次循环增加多少涨跌幅度
ONCE_CASH = 6000 # 每次交易买卖的大概资金
INITIAL_CASH = 50000 # 初始建仓金额

STOCK_CODE = "601688" # 模拟的股票代码
STOCK_COUNT = 550 # 股票交易次数
STOCK_DATE = "2024-07-26" # 股票交易日期 2023-08-09

# 持仓数据结构字段
INVEST_PRICE = "price" # 交易的价格
INVEST_CASH = "cash" # 交易金额
INVEST_SHARES = "shares" # 交易股份数量， 单位：手
INVEST_DATETIME = "datetime" # 交易日期

# 模拟结果数据字段
RESULT_PROFIT = "profit" # 总的收益
RESULT_SELL_COUNT = "sell_count" # 总卖出次数
RESULT_INIT_COUNT = "init_count" # 初始建仓次数
RESULT_INIT_CASH = "init_cash" # 初始建仓金额
RESULT_INIT_PRICE = "init_price" # 初始建仓价格
RESULT_FIN_COUNT = "finally_count" # 最终持仓次数
RESULT_FIN_CASH = "finally_cash" # 最终持仓金额
RESULT_FIN_AVER_PRICE = "finally_average_price" # 最终持仓均价
RESULT_MAX_COUNT = "max_count" # 最大持仓数量
RESULT_MAX_CASH = "max_cash" # 最大持仓金额
RESULT_MISSING_COUNT = "missing_sell_count" # 错过交易次数

def print_red(p_str):
    print('\033[1;31;40m' + p_str + '\033[0m')
    
def simulated_invest(df, target_change):
    print(f"******************************* 模拟开始（{target_change}） *******************************")
    simulated_result = {}
    # 持仓列表
    invest_list = []
    # 盈利列表
    profit_list = []
    # 最大持仓份数
    max_invest_count = 0
    # 最大持仓金额
    max_invest_cash = 0
    # 因无筹码，导致无法卖出的次数
    missing_sell_count = 0

    # 初始一共建仓的次数
    initial_buy_count = int(INITIAL_CASH / ONCE_CASH)
    # 初始每次建仓的价格、股份数、金额
    initial_once_buy_price = df.iloc[0]['open']
    initial_once_buy_shares = int(ONCE_CASH / (initial_once_buy_price * 100.0))
    initial_once_buy_cash = int(initial_once_buy_shares * initial_once_buy_price * 100.0)
    initial_once_buy_datetime = df.index[0].date()

    for i in range(0, initial_buy_count):
        initial_invest = {INVEST_DATETIME: initial_once_buy_datetime, INVEST_PRICE: initial_once_buy_price, INVEST_SHARES: initial_once_buy_shares, INVEST_CASH: initial_once_buy_cash}
        invest_list.append(initial_invest)

    max_invest_count = initial_invest_count = len(invest_list)
    max_invest_cash = initial_invest_cash = sum(item[INVEST_CASH] for item in invest_list)
    # print(f"初始建仓: {invest_list}")

    # sys.exit() # 直接结束脚本

    # 开始遍历每天的股票数据，根据涨跌幅进行买卖
    for i in range(1, len(df)):
        # 计算当天的涨跌幅度
        previous_close = df.iloc[i-1]['close']
        current_close = df.iloc[i]['close']
        change = round((current_close - previous_close) / previous_close * 100.0, 2) # 四舍五入保留两位小数
        # print(f"{df.index[i].data()} -> 涨跌幅: {change}")
        # 如果涨幅大于最大设定幅度，开始寻找最低的买入价格的那笔进行卖出，并计算盈利
        if (change >= target_change):
            # 先判断是否还有持仓筹码
            if (len(invest_list) == 0):
                missing_sell_count += 1
                print("=============== 已无筹码，错过交易机会 ============")
                continue
            # 使用 min() 函数和 lambda 函数找到 price 最小的字典
            min_price_data = min(invest_list, key=lambda x: x[INVEST_PRICE])
            # 打印找到的最小 price 的字典
            # print(f"价格最低的那次交易: {min_price_data}")
            # 从列表中删除找到的字典
            invest_list.remove(min_price_data)
            # 与当前收盘价进行对比计算收益
            profit = int(round((current_close - min_price_data[INVEST_PRICE]) * min_price_data[INVEST_SHARES] * 100, 0))
            profit = profit - 5 # 收益减去5元的佣金
            # print(f"卖出一次股票收益: {profit}")
            # 添加到收益列表中用于最终的收益计算
            profit_list.append(profit)
        # 如果跌幅大于最大设定跌幅，开始买入一份股票
        if (change <= -1*target_change):
            once_invest_price = current_close
            once_invest_shares = int(ONCE_CASH / (current_close * 100.0))
            once_invest_cash = int(once_invest_shares * current_close * 100)
            once_invest_datetime = df.index[i].date()
            once_invest = {INVEST_DATETIME: once_invest_datetime, INVEST_PRICE: once_invest_price, INVEST_SHARES: once_invest_shares, INVEST_CASH: once_invest_cash}
            # print(f"买入一次股票: {once_invest}")
            invest_list.append(once_invest)
            total_cash = sum(item[INVEST_CASH] for item in invest_list)
            # print(f"当前持仓份数: {len(invest_list)}, 持仓金额: {total_cash}")
            # 重置最大的持仓数和持仓金额
            max_invest_count = max(max_invest_count, len(invest_list))
            max_invest_cash = max(max_invest_cash, total_cash)
    
    # 初始建仓基本情况
    print(f"======== 初始 === 建仓份数: {initial_invest_count}, 建仓总金额: {initial_invest_cash}, 建仓均价: {initial_once_buy_price} ========")
    print(f"总交易收益表: {profit_list}")
    total_sell_count = len(profit_list) # 一共卖出次数
    total_profit = sum(profit_list) # 总收益金额
    print_red(f"======== 总交易次数: {total_sell_count}, 总交易收益金额: {total_profit}, 错过交易次数: {missing_sell_count} ========")
    print(f"======== 历史最大持仓数: {max_invest_count}, 历史最大持仓金额: {max_invest_cash} ========")

    total_invest_cash = sum(item[INVEST_CASH] for item in invest_list)
    # 计算最终持仓均价
    total_invest_shares = sum(item[INVEST_SHARES] for item in invest_list)
    average_price = 0
    if (total_invest_shares != 0):
        average_price = round(total_invest_cash / total_invest_shares / 100, 2)
    print(f"======== 最终持仓数: {len(invest_list)}, 最终持仓金额: {total_invest_cash}, 持仓均价: {average_price} ========")

    if (len(invest_list) == 0):
        print(f"======== 最终持仓列表: []")
    else:
        # 将数据列表转换为 DataFrame
        invest_df = pd.DataFrame(invest_list)
        # 将 'datetime' 列转换为日期时间格式
        invest_df['datetime'] = pd.to_datetime(invest_df['datetime'])
        # 将 'datetime' 列设置为索引列
        invest_df.set_index('datetime', inplace=True)
        invest_df.index.name = ""
        # print(f"======== 最终持仓列表:")
        # print(invest_df)
    print(f"******************************* 模拟结束（{target_change}） *******************************")
    simulated_result[RESULT_PROFIT] = total_profit
    simulated_result[RESULT_SELL_COUNT] = total_sell_count
    simulated_result[RESULT_INIT_COUNT] = initial_invest_count
    simulated_result[RESULT_INIT_CASH] = initial_invest_cash
    simulated_result[RESULT_INIT_PRICE] = initial_once_buy_price
    simulated_result[RESULT_FIN_COUNT] = len(invest_list)
    simulated_result[RESULT_FIN_CASH] = total_invest_cash
    simulated_result[RESULT_FIN_AVER_PRICE] = average_price
    simulated_result[RESULT_MAX_COUNT] = max_invest_count
    simulated_result[RESULT_MAX_CASH] = max_invest_cash
    simulated_result[RESULT_MISSING_COUNT] = missing_sell_count
    return simulated_result


df=get_price(f'sh{STOCK_CODE}',frequency='1d',count=STOCK_COUNT, end_date=STOCK_DATE, tx_channel=True)   #可以指定结束日期，获取历史行情 228 2023-08-09
print('股票数据\n',df)

# 绘制表格需要的数据
SHEET_CHANGE = [] # 涨跌幅列表，作为表格的横坐标
SHEET_PROFIT = [] # 收益列表，作为表格的纵坐标
# 生成从 MIN_CHANGE 到 MAX_CHANGE，步长为 0.1 的数列
changes = np.arange(MIN_CHANGE, MAX_CHANGE + CHANGE_STEP, CHANGE_STEP)
result = []
# 使用 for 循环进行迭代
for change in changes:
    SHEET_CHANGE.append(change)
    result.append(simulated_invest(df, change))

SHEET_PROFIT = [item[RESULT_PROFIT] for item in result]
print(SHEET_CHANGE)
print(SHEET_PROFIT)
CLOSE=df.close.values

#------------------------------------------ 图表显示 ---------------------------------------#
# 创建图形和子图， ******** 一张图
# plt.figure(figsize=(15, 8))
# # 绘制股票涨跌幅
# plt.plot(SHEET_CHANGE, SHEET_PROFIT, marker='o', linestyle='-', color='b', label='Profits')
# # 在每个折线点上显示对应的 info
# for i in range(len(result)):
#     plt.annotate(f"T: {result[i][RESULT_PROFIT]}-{result[i][RESULT_SELL_COUNT]} \n F: {result[i][RESULT_FIN_CASH]}-{result[i][RESULT_FIN_COUNT]}-{result[i][RESULT_FIN_AVER_PRICE]} \n H: {result[i][RESULT_MAX_CASH]}-{result[i][RESULT_MAX_COUNT]}", (SHEET_CHANGE[i], SHEET_PROFIT[i]), textcoords="offset points", xytext=(0,10), ha='center', color='purple')
# # 添加标题和标签
# plt.title(f"{STOCK_CODE}", fontsize=10)
init_info = f"Init: count={result[0][RESULT_INIT_COUNT]}, funds={result[0][RESULT_INIT_CASH]}, price={result[0][RESULT_INIT_PRICE]}, day={df.index[0].date()} ~ {df.index[-1].date()} ({len(df)})"
# plt.xlabel(init_info, fontsize=14)
# plt.ylabel('Profit', fontsize=14)
# # 显示图例
# plt.legend()
# # 显示网格
# plt.grid(True)
# # 显示图形
# plt.show()

# 创建一个新的图表和两个子图，******** 两张图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))

# 绘制第一个子图 (SHEET_CHANGE vs SHEET_PROFIT)
ax1.plot(SHEET_CHANGE, SHEET_PROFIT, marker='o', linestyle='-', color='tab:blue', label='PROFIT')
ax1.set_xlabel(f"code: {STOCK_CODE}")
ax1.set_ylabel('SHEET_PROFIT')
ax1.legend()
ax1.grid()
# 在每个折线点上显示对应的 info
for i in range(len(result)):
    ax1.annotate(f"T: {result[i][RESULT_PROFIT]}-{result[i][RESULT_SELL_COUNT]}-{result[i][RESULT_MISSING_COUNT]} \n F: {result[i][RESULT_FIN_CASH]}-{result[i][RESULT_FIN_COUNT]}-{result[i][RESULT_FIN_AVER_PRICE]} \n H: {result[i][RESULT_MAX_CASH]}-{result[i][RESULT_MAX_COUNT]}", (SHEET_CHANGE[i], SHEET_PROFIT[i]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontsize=8)

# 绘制第二个子图 (df.index vs CLOSE)
ax2.plot(df.index, CLOSE, color='tab:red', label='STOCK')
ax2.set_xlabel("Date")
ax2.set_ylabel('CLOSE')
ax2.legend()
ax2.grid()

# 设置图表标题
fig.suptitle(init_info, fontsize=14)

# 显示图表
plt.show()