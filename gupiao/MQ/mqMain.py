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

# 输入日期
date_str = "2024-12-25"
date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
print(f"{is_fourth_wednesday(date)}")

e_date = "2025-01-05"

df=get_price('sh000001',frequency='1d',count=20, end_date=e_date, tx_channel=False)
print('上证指数日线行情\n',df)

start_date = df.index[0]
end_date = pd.to_datetime(e_date)
print(f"时间范围: {start_date.date()} ~ {end_date.date()}")

# 遍历每一天
current_date = start_date
while current_date <= end_date:
    # print(current_date)
    if is_fourth_wednesday(current_date.date()):
        print(f"行权日: {current_date}")
    # 每次递增一天
    current_date += datetime.timedelta(days=1)