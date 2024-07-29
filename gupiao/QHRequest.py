# -*- coding: utf-8 -*-
# -------------- 期货数据请求 https://www.quheqihuo.com/quote/hq-635.html -------------- #
import json, requests, os
import re
import pandas as pd
from datetime import datetime

# 设置显示选项以完整打印数据
pd.set_option("display.max_rows", None)  # 显示所有行
pd.set_option("display.max_columns", None)  # 显示所有列
pd.set_option("display.width", None)  # 设置自动调整宽度
pd.set_option("display.max_colwidth", None)  # 设置列宽为无限制


def get_price_day_online(code, cachefile):
    url = f"https://api.jijinhao.com/sQuoteCenter/kDataList.htm?code=JO_{code}&pageSize=100"
    hds = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.quheqihuo.com/quote/czce-sam.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
    res_data = requests.get(url, headers=hds).content.decode('utf-8')
    # 使用正则表达式提取 JSON 字符串
    json_str = re.search(r'\{.*\}', res_data).group()
    # 将 JSON 字符串转换为字典
    json_data = json.loads(json_str)
    # print(json_data)
    # 第一个数组是期货日k，第二和第三应该是月k和周k
    qh_list = json_data["data"][0]
    # 将 JSON 数据写入本地文件
    with open(cachefile, 'w', encoding='utf-8') as file:
        json.dump(qh_list, file, ensure_ascii=False, indent=4)
    return qh_list
    
def get_price_day(code, start_date, end_date, cache=True): # cache 指是否要使用缓存，每天的数据都是固定的，抓取后可存在本地，下次获取直接从本地取
    if cache:
        # 获取当天的日期
        today_date = datetime.now().strftime('%Y-%m-%d')
        filename = f"./gupiao/cache/{code}-{today_date}.json"
        print(f"缓存目录：{filename}")

        # 检查文件是否存在
        if os.path.exists(filename):
            # 如果文件存在，从文件中读取 JSON 数据
            with open(filename, 'r', encoding='utf-8') as file:
                qh_list = json.load(file)
                print(f"数据从本地文件中读取：{qh_list[0]}, {qh_list[-1]}")
        else:
            qh_list = get_price_day_online(code, filename)
            print(f"数据从服务端获取：{qh_list[0]}, {qh_list[-1]}")
    else:
        qh_list = get_price_day_online(code, filename)
        print(f"数据从服务端获取：{qh_list[0]}, {qh_list[-1]}")
        
    df = pd.DataFrame(qh_list, columns=["day", "open", "close", "high", "low", "volume"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df.day = pd.to_datetime(df.day)
    df.set_index(["day"], inplace=True)
    df.index.name = ""  # 处理索引
    
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df[mask]
    return filtered_df

if __name__ == "__main__":
    df = get_price_day("233773", "2024-07-22", "2024-07-29") # 纯碱主连：233773，去接口网站抓取数据 URL 中会有对应的 Code
    print(df)