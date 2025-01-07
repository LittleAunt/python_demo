# -*- coding: utf-8 -*-
# -------------- 期货数据请求 https://www.quheqihuo.com/quote/hq-635.html -------------- #
import json, requests, os
import re
import pandas as pd
from datetime import datetime
import time
import threading

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
    # print(f"开始日期：{start_date}，结束日期：{end_date}")
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
                # print(f"数据从本地文件中读取：{qh_list[0]}, {qh_list[-1]}")
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
    # 过滤想要的日期时间段数据
    mask = (df.index >= start_date) & (df.index <= end_date)
    filtered_df = df[mask]
    return filtered_df

# 曲合期货网，获取对应期货的实时交易价格数据
def getRealtimeData(code):
    # 获取当前时间戳（毫秒级别）
    timestamp_ms = int(time.time() * 1000)
    url = f"https://api.jijinhao.com/sQuoteCenter/realTime.htm?code=JO_{code}&_={timestamp_ms}"
    hds = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.quheqihuo.com/quote/czce-sam.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
    res_data = requests.get(url, headers=hds).content.decode('utf-8')
    match = re.search(r'"([^"]*)"', res_data)
    result = {}
    if match:
        content = match.group(1)  # 提取 "" 内的内容
        values = content.split(",")  # 按 , 分割字符串内容
        # print(f"期货实时数据：{values}")
        result['open'] = float(values[-5])
        result['b1'] = float(values[-7])
        result['s1'] = float(values[-6])
    return result

prs = {
    "http": "127.0.0.1:8888",
    "https": "127.0.0.1:8888",
}

qiq_realtime_data = {}
# 东方财富，获取实时期权交易价格数据
def getQIQRealtimeData(code, callback):
    url = f"https://36.futsseapi.eastmoney.com/sse/141_{code}_qt?token=1101ffec61617c99be287c1bec3085ff&field=name,sc,dm,p,zsjd,zdf,zde,utime,o,zjsj,qrspj,h,l,mrj,mcj,vol,cclbh,zt,dt,np,wp,ccl,rz,cje,mcl,mrl,jjsj,j,lb,zf"
    hds = {
        "Accept": "text/event-stream",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-control": "no-cache",
        "Connection": "keep-alive",
        "Host": "36.futsseapi.eastmoney.com",
        "Origin": "https://quote.eastmoney.com",
        "Referer": "https://quote.eastmoney.com/option/141.SA501P1500.html",
        "Sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-ch-ua-mobile": "?0",
        "Sec-ch-ua-platform": '"macOS"',
        "Sec-fetch-dest": "empty",
        "Sec-fetch-mode": "cors",
        "Sec-fetch-site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
    
    def stream():
        with requests.get(url, headers=hds, stream=True) as response:
            response.encoding = 'utf-8'  # 指定编码格式为 utf-8
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    value = line[len("data:"):].strip()  # 提取数据内容
                    # 将 json 字符串转换为 Python 字典
                    data = json.loads(value)
                    print(f'期权实时数据：getQIQRealtimeData -> {data}')       
                    if "qt" in data:
                        qt_data = data["qt"]
                        data_changed = False
                        global qiq_realtime_data
                        if "o" in qt_data and qt_data["o"] != "-":
                            qiq_realtime_data["open"] = qt_data["o"]
                            data_changed = True
                        if "mrj" in qt_data and qt_data["mrj"] != "-":
                            qiq_realtime_data["b1"] = qt_data["mrj"]
                            data_changed = True
                        if "mcj" in qt_data and qt_data["mcj"] != "-":
                            qiq_realtime_data["s1"] = qt_data["mcj"]
                            data_changed = True
                        # 数据发生改变，且所有字段都不为空
                        if data_changed and "open" in qiq_realtime_data and "b1" in qiq_realtime_data and "s1" in qiq_realtime_data:
                            callback(qiq_realtime_data)
    # 启动新线程进行非阻塞请求
    thread = threading.Thread(target=stream)
    # thread.daemon = True  # 设置为守护线程，使其随主线程退出
    thread.start()

if __name__ == "__main__":
    df = get_price_day("233773", "2024-07-22", "2024-07-29") # 纯碱主连：233773，去接口网站抓取数据 URL 中会有对应的 Code
    print(df)