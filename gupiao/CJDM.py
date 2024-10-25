# -*- coding: utf-8 -*-
# -------------------------- 根据纯碱主连的技术买卖点进行期权的买卖 --------------------------#
from CJZLSimulated import *
import pandas as pd
from decimal import Decimal, getcontext
from  QHRequest import *
from utils import *

# 设置精度
getcontext().prec = 28

SA_DATA_PATH = "./gupiao/QIQDATA/SA/data/{}.txt"
KEY_START_DATE = "start_date"
KEY_END_DATE = "end_date"
KEY_HY_CODE = "hy_code" # 合约代码前缀

# 期货每日买卖方向和开盘收盘价格
QH_DATE = "date"
QH_TYPE = "type"
QH_OPEN = "open"
QH_CLOSE = "close"

QIQ_RECORD_DATE = "date" # 交易日期
QIQ_RECORD_HY_CODE = "code" # 交易合约代码
QIQ_RECORD_PRICE = "price" # 交易价格
QIQ_RECORD_AMOUNT = "amount" # 交易金额
QIQ_RECORD_COUNT = "count" # 交易数量
QIQ_RECORD_TYPE = "type" # 交易类型，买、卖
QIQ_RECORD_PROFIT = "profit" # 收益

CJZL_LIST = [
    # {KEY_START_DATE: "2023-10-20", KEY_END_DATE: "2023-12-04", KEY_HY_CODE: "SA401"},  
    # {KEY_START_DATE: "2023-12-05", KEY_END_DATE: "2024-03-22", KEY_HY_CODE: "SA405"},
    # {KEY_START_DATE: "2024-03-25", KEY_END_DATE: "2024-08-13", KEY_HY_CODE: "SA409"}, 
    {KEY_START_DATE: "2024-08-15", KEY_END_DATE: "2024-10-24", KEY_HY_CODE: "SA501"}
]

def simulated_all():
    result_list = []
    start_index = 0
    for i in range(start_index, len(CJZL_LIST)):
        result = simulated_invest(CODE_ZL, CJZL_LIST[i][KEY_START_DATE], CJZL_LIST[i][KEY_END_DATE], 1, TYPE_P, False)
        result_list.append(result)
    return result_list

def get_price_from_code(code):
    match = re.search(r'[CP](\d+)', code)  # 匹配 C 或 P 后面的数字
    if match:
        return match.group(1) # 获取匹配的数字
    else:
        return None
    
# 定位到对应的价格合约
def get_target_hy(df, qh_open):
    print(f"##### qh_open: {qh_open}")
    # 合约每 20 块钱一个档位
    for i in range(0, len(df)):
        code = df.iloc[i]['code']
        hy_price = float(get_price_from_code(code))
        if abs(qh_open - hy_price) < 20:
            return df.iloc[i]
    # 合约每 40 块钱一个档位
    for i in range(0, len(df)):
        code = df.iloc[i]['code']
        hy_price = float(get_price_from_code(code))
        if abs(qh_open - hy_price) < 40:
            return df.iloc[i]
    print(f"##### return None")
    print(f"### df \n{df}")
    return None

def convertBuylist(qh_records):
    buylist = []
    for i in range(0, len(qh_records) - 1):
        c_record = qh_records[i]
        n_record = qh_records[i + 1]
        c_type = c_record[INVEST_TYPE]
        c_date = c_record[RECORD_DATE] + timedelta(days=1)
        n_date = n_record[RECORD_DATE]
        # 遍历日期
        while c_date <= n_date:
            date_str = c_date.strftime('%Y-%m-%d')
            print(date_str)  # 打印日期
            df = get_price_day(CODE_ZL, date_str, date_str)
            if len(df) != 0:
                buy_data = {
                    QH_DATE: date_str,
                    QH_TYPE: c_type,
                    QH_OPEN: df.iloc[0].open,
                    QH_CLOSE: df.iloc[0].close
                }
                buylist.append(buy_data)
                print(buy_data)
            c_date += timedelta(days=1)  # 增加一天  
    return buylist
    
def simulated_qiq(qh_records, code):
    # 先根据期货交易记录，生成每日的买卖的预期列表
    buylist = convertBuylist(qh_records)
    # 获取期权的数据
    file = SA_DATA_PATH.format(code)
    print(file)
    df = pd.read_csv(file, sep='|', skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    
    dm_profit_list = [] # 收益列表
    # 遍历每个日期进行期货和期权的对买
    for qhdata in buylist:
        r_date = qhdata[QH_DATE]
        r_type = qhdata[QH_TYPE]
        # 过滤出对应的日期数据
        filtered_df = df[df['date'] == r_date]
        # 再过滤对应的认购、认沽合约数据
        filtered_df_d = filtered_df[filtered_df['code'].str.startswith("{}C".format(code))]
        filtered_df_k = filtered_df[filtered_df['code'].str.startswith("{}P".format(code))]
        # 1. 先计算期货当天买卖收益
        qh_profit = ((qhdata[QH_CLOSE]) - qhdata[QH_OPEN]) * 20
        if r_type == TYPE_K:
            qh_profit *= -1
        # 2. 再计算期权当天的买卖收益，如果期货买多，期权则认沽，期货买空，期权认购
        if r_type == TYPE_D or r_type == TYPE_P:
            hy_data = get_target_hy(filtered_df_k, qhdata[QH_OPEN])
        if r_type == TYPE_K:
            hy_data = get_target_hy(filtered_df_d, qhdata[QH_OPEN])
        hy_profit = (hy_data['close'] - hy_data['open']) * 20 * 2
        # 3. 期货与期权的总收益
        total_profit = qh_profit + hy_profit
        dm_profit_list.append({
            "date": r_date,
            "total_profit": total_profit,
            "qh_profit": qh_profit,
            "hy_profit": hy_profit
        })
        if total_profit >= 0:
            print_red(f"日期: {r_date}, 总收益: {total_profit}, 期货收益: {qh_profit}, 期权收益: {hy_profit}")
        else:
            print_green(f"日期: {r_date}, 总收益: {total_profit}, 期货收益: {qh_profit}, 期权收益: {hy_profit}")
            
    # 计算总的认购和认沽收益
    all_profit = sum(item["total_profit"] for item in dm_profit_list)
    print(f"#### 总收益：{all_profit}")
    return all_profit

def simulated_qiq_all():
    # 根据纯碱主联的走势找出每个买卖点
    result_list = simulated_all()
    profit_list = []
    for i in range(0, len(CJZL_LIST)):
        qh_records = result_list[i][RESULT_RECORDS]
        cjzl = CJZL_LIST[i]
        code = cjzl[KEY_HY_CODE]
        profit = simulated_qiq(qh_records, code)
        profit_list.append(profit)
    print("########################################################")
    print(f"#### 所有主连收益列表：{profit_list}")
    all_profit = sum(profit_list)
    print(f"#### 所有主连总收益：{all_profit}")
    return all_profit
    
MIN_CHANGE = Decimal('0.5') 
MAX_CHANGE = Decimal('10')
CHANGE_STEP = Decimal('0.5')
   
if __name__ == "__main__":
    # changes = np.arange(MIN_CHANGE, MAX_CHANGE + CHANGE_STEP, CHANGE_STEP)
    # result = []
    # # 使用 for 循环进行迭代
    # for change in changes:
    #     HY_PRICE = change
    #     result.append(simulated_qiq_all())
    # print(f"#### 收益列表: {result}")
    
    simulated_qiq_all()
    # simulated_qiq(None, "SA501")