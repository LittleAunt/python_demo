import sys
import os

# 获取脚本文件所在目录的父目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的绝对路径
parent_dir = os.path.dirname(current_dir)  # 获取父目录路径
# 将父目录路径添加到 sys.path 中
sys.path.append(parent_dir)

from Ashare import *
import akshare as ak
import datetime
import calendar

# 判断某个日期是否为该月的第四个星期三
def is_fourth_wednesday(date: datetime.date) -> bool:
    # 获取该日期所在月的所有星期三
    year = date.year
    month = date.month
    
    # 获取该月1号的星期几
    first_day_of_month = datetime.date(year, month, 1)
    first_weekday = first_day_of_month.weekday()  # 0是周一，6是周日

    # 计算该月所有的星期三的日期
    wednesdays = []
    for day in range(1, calendar.monthrange(year, month)[1] + 1):  # 遍历该月所有天数
        current_date = datetime.date(year, month, day)
        if current_date.weekday() == 2:  # 2 是星期三
            wednesdays.append(current_date)

    # 判断是否为第四个星期三
    if len(wednesdays) >= 4 and wednesdays[3] == date:
        return True
    return False

# 获取行权日对应的交易记录，如果没有取下一个交易日
def getXQRecord(t_date, df):
    for i in range(0, len(df)):
        if df.index[i] >= t_date:
            return df.iloc[i]
        
# 获取行权日下一个交易日的交易记录
def getXQNextRecord(t_date, df):
    xq_record = getXQRecord(t_date, df)
    for i in range(0, len(df)):
        if df.index[i] > xq_record.name:
            return df.iloc[i]

# 计算每个涨幅档位的个数
def count_ranges(result_list):
    # 初始化各个范围的计数
    ranges = {
        "0-2": 0,
        "2-4": 0,
        "4-6": 0,
        "6-8": 0,
        "8-10": 0,
        "10+": 0
    }

    # 遍历数字数组
    for result in result_list:
        if 0 <= abs(result["涨幅"]) < 2:
            ranges["0-2"] += 1
        elif 2 <= abs(result["涨幅"]) < 4:
            ranges["2-4"] += 1
        elif 4 <= abs(result["涨幅"]) < 6:
            ranges["4-6"] += 1
        elif 6 <= abs(result["涨幅"]) < 8:
            ranges["6-8"] += 1
        elif 8 <= abs(result["涨幅"]) < 10:
            ranges["8-10"] += 1
        else:  # 10 以上的数字
            ranges["10+"] += 1

    # 计算每个范围的百分比
    total_count = len(result_list)
    ranges_with_percentage = {}
    for key, count in ranges.items():
        percentage = (count / total_count) * 100 if total_count > 0 else 0
        ranges_with_percentage[key] = {
            "count": count,
            "percentage": round(percentage, 2)  # 保留两位小数
        }

    return ranges_with_percentage
    
# 输入日期
# date_str = "2024-12-25"
# date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
# print(f"{is_fourth_wednesday(date)}")

e_date = "2025-01-11"

df=get_price('sh000001',frequency='1d',count=2600, end_date=e_date, tx_channel=False)
print('上证指数日线行情\n',df)

start_date = df.index[0]
end_date = pd.to_datetime(e_date)
print(f"时间范围: {start_date.date()} ~ {end_date.date()}")

# 遍历每一天，确定每一个行权日
xq_date_list = []
current_date = start_date
while current_date <= end_date:
    # print(current_date)
    if is_fourth_wednesday(current_date.date()):
        xq_date_list.append(current_date)
        
    # 每次递增一天
    current_date += datetime.timedelta(days=1)

record = getXQRecord(xq_date_list[0], df)
print(f"record  {record.name}")
# 遍历交易记录，计算每个行权日当月涨幅情况
result_list = []
for i in range(1, len(xq_date_list)): # 第一个行权日数据不完整，所以从第二个开始
    first_record = getXQNextRecord(xq_date_list[i - 1], df)
    end_record = getXQRecord(xq_date_list[i], df)
    zf = (end_record.close - first_record.open) / first_record.open
    zf_p = round(zf * 100, 2)
    result_list.append({"行权日": end_record.name.date(), "涨幅": zf_p})
    
for r in result_list:
    print(r)

# 各个涨幅范围的月份个数
range_count = count_ranges(result_list)
print(f"一共 {len(result_list)} 个月")
print(range_count)