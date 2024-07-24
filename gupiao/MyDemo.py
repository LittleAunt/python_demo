from  Ashare import *
import sys
import pandas as pd

ONCE_INVEST = 11000 # 每次交易买卖的大概资金
MAX_CHANGE = 1.5 # 每次交易依据的涨跌幅度
INITIAL_INVEST = 55000 # 初始建仓金额

# 持仓数据结构字段
INVEST_PRICE = "price" # 交易的价格
INVEST_CASH = "cash" # 交易金额
INVEST_SHARES = "shares" # 交易股份数量， 单位：手
INVEST_DATETIME = "datetime" # 交易日期


df=get_price('sh601688',frequency='1d',count=228)   #可以指定结束日期，获取历史行情 228
# print('华泰历史行情\n',df)

# 持仓列表
invest_list = []
# 盈利列表
profit_list = []
# 最大持仓份数
max_invest_count = 0
# 最大持仓金额
max_invest_cash = 0

# 初始一共建仓的次数
initial_buy_count = int(INITIAL_INVEST / ONCE_INVEST)
# 初始每次建仓的价格、股份数、金额
initial_once_buy_price = df.iloc[0]['open']
initial_once_buy_shares = int(ONCE_INVEST / (initial_once_buy_price * 100.0))
initial_once_buy_cash = int(initial_once_buy_shares * initial_once_buy_price * 100.0)
initial_once_buy_datetime = df.index[0].strftime('%Y-%m-%d')

for i in range(0, initial_buy_count):
    initial_invest = {INVEST_DATETIME: initial_once_buy_datetime, INVEST_PRICE: initial_once_buy_price, INVEST_SHARES: initial_once_buy_shares, INVEST_CASH: initial_once_buy_cash}
    invest_list.append(initial_invest)

max_invest_count = initial_invest_count = len(invest_list)
max_invest_cash = initial_invest_cash = sum(item[INVEST_CASH] for item in invest_list)
print('############ 初始建仓 ###########')
print(invest_list)

# sys.exit() # 直接结束脚本

# 开始遍历每天的股票数据，根据涨跌幅进行买卖
for i in range(1, len(df)):
    # 计算当天的涨跌幅度
    previous_close = df.iloc[i-1]['close']
    current_close = df.iloc[i]['close']
    change = round((current_close - previous_close) / previous_close * 100.0, 2) # 四舍五入保留两位小数
    print(f"{df.index[i].strftime('%Y-%m-%d')} -> 涨跌幅: {change}")
    # 如果涨幅大于最大设定幅度，开始寻找最低的买入价格的那笔进行卖出，并计算盈利
    if (change >= MAX_CHANGE):
        # 先判断是否还有持仓筹码
        if (len(invest_list) == 0):
            print("=============== 已无筹码，错过交易机会 ============")
            continue
        # 使用 min() 函数和 lambda 函数找到 price 最小的字典
        min_price_data = min(invest_list, key=lambda x: x[INVEST_PRICE])
        # 打印找到的最小 price 的字典
        print(f"价格最低的那次交易: {min_price_data}")
        # 从列表中删除找到的字典
        invest_list.remove(min_price_data)
        # 与当前收盘价进行对比计算收益
        profit = int(round((current_close - min_price_data[INVEST_PRICE]) * min_price_data[INVEST_SHARES] * 100, 0))
        profit = profit - 5 # 收益减去5元的佣金
        print(f"******* 本次交易收益: {profit}")
        # 添加到收益列表中用于最终的收益计算
        profit_list.append(profit)
    # 如果跌幅大于最大设定跌幅，开始买入一份股票
    if (change <= -1*MAX_CHANGE):
        once_invest_price = current_close
        once_invest_shares = int(ONCE_INVEST / (current_close * 100.0))
        once_invest_cash = int(once_invest_shares * current_close * 100)
        once_invest_datetime = df.index[i].strftime('%Y-%m-%d')
        once_invest = {INVEST_DATETIME: once_invest_datetime, INVEST_PRICE: once_invest_price, INVEST_SHARES: once_invest_shares, INVEST_CASH: once_invest_cash}
        print(f"买入一次股票: {once_invest}")
        invest_list.append(once_invest)
        total_cash = sum(item[INVEST_CASH] for item in invest_list)
        print(f"当前持仓份数: {len(invest_list)}, 持仓金额: {total_cash}")
        # 重置最大的持仓数和持仓金额
        max_invest_count = max(max_invest_count, len(invest_list))
        max_invest_cash = max(max_invest_cash, total_cash)
 
       
# 最终持仓列表
print("############ 交易结束 ###########")
# 初始建仓基本情况
print(f"======== 初始 === 建仓份数: {initial_invest_count}, 建仓总金额: {initial_invest_cash}, 建仓均价: {initial_once_buy_price} ========")
print(f"总交易收益表: {profit_list}")
total_sell_count = len(profit_list) # 一共卖出次数
total_profit = sum(profit_list) # 总收益金额
print(f"======== 总交易次数: {total_sell_count}, 总交易收益金额: {total_profit} ========")
print(f"======== 历史最大持仓数: {max_invest_count}, 历史最大持仓金额: {max_invest_cash} ========")

total_invest_cash = sum(item[INVEST_CASH] for item in invest_list)
# 计算最终持仓均价
total_invest_shares = sum(item[INVEST_SHARES] for item in invest_list)
average_price = round(total_invest_cash / total_invest_shares / 100, 2)
print(f"======== 最终持仓数: {len(invest_list)}, 最终持仓金额: {total_invest_cash}, 持仓均价: {average_price} ========")

# 将数据列表转换为 DataFrame
invest_df = pd.DataFrame(invest_list)
# 将 'datetime' 列转换为日期时间格式
invest_df['datetime'] = pd.to_datetime(invest_df['datetime'])
# 将 'datetime' 列设置为索引列
invest_df.set_index('datetime', inplace=True)
invest_df.index.name = ""
print(f"======== 最终持仓列表:")
print(invest_df)