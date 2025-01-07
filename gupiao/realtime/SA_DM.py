# -*- coding: utf-8 -*-
# -------------------------- 根据纯碱期货期权的实时数据获取差价，计算收益 --------------------------#
import sys
import os
# 获取项目根目录路径并添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from CodeList import *
from  QHRequest import *
import threading
import time
import logging
from utils import *

# 期货是否是做多，确定买卖的方向
DUO = True
QIQ_CODE = "SA501P1520"
QIQ_DATA = None

# 定义下载目录
current_path = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_DIRECTORY = current_path + '/logs'

# 确保下载目录存在
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)
    
# 设置日志记录器
logging.basicConfig(
    filename=f'{DOWNLOAD_DIRECTORY}/{QIQ_CODE}_{datetime.now().strftime('%Y-%m-%d')}.log',      # 日志文件名
    filemode='a',            # 追加模式写入（'w' 则为覆盖模式）
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    level=logging.INFO        # 设置日志级别
)

# 1. 获取期货的实时收益
def getQHProfit():
    result = {}
    qh_data = getRealtimeData(CODE_SA_ZL)
    logstr = f"期货数据: {qh_data}"
    print(logstr)
    logging.info(logstr)
    if DUO:
        profit = (qh_data['b1'] - qh_data['open']) * 20
        result['price'] = qh_data['b1']
        result['profit'] = profit
    else:
        profit = (qh_data['s1'] - qh_data['open']) * 20 * -1
        result['price'] = qh_data['s1']
        result['profit'] = profit
    return result

def getQIQProfit():
    if QIQ_DATA:
        profit = (QIQ_DATA['b1'] - QIQ_DATA['open']) * 20 * 2
        return {
            'price': QIQ_DATA['b1'],
            'profit': profit
        }
    return None

def cal_profit():
    qh_profit = getQHProfit()
    qiq_profit = getQIQProfit()
    if qiq_profit:
        profit = qh_profit['profit'] + qiq_profit['profit']
        # 打印并缓存收益的日志信息，用于后续的分析
        current_time = datetime.now().strftime("%H:%M:%S")
        logstr = f"总收益: {profit}, 期货: {qh_profit}, 期权: {qiq_profit}"
        logging.info(logstr)
        if profit > 0:
            print_red(f"{current_time} {logstr}")
        else:
            print_green(f"{current_time} {logstr}")

def handle_qiq_data(data):
    global QIQ_DATA
    QIQ_DATA = data
    logstr = f"***期权数据: {QIQ_DATA}"
    print(logstr)
    logging.info(logstr)
    cal_profit()
    
def startQIQDataReceiver():
    getQIQRealtimeData(QIQ_CODE, handle_qiq_data)
    
def cal_profit_task():
    while True:
        cal_profit()
        time.sleep(5)
    
def startCalThread():
    # 创建并启动线程
    cal_thread = threading.Thread(target=cal_profit_task)
    # cal_thread.daemon = True  # 设置为守护线程，主程序结束后该线程自动退出
    cal_thread.start()
  
if __name__ == "__main__":
    # 启动期权数据接收器
    startQIQDataReceiver()
    # 创建子线程，每隔 5s 执行一次收益计算
    startCalThread()
    # cal_profit_task()