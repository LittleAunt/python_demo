from BaseBC import BaseBC
from dic_ob import OBDic
import requests
import json
from config import USER_AUTH_OB
from config import MODE_GQ
import time
import bc_print

# 用户身份验证。接口中 request_headers 中的 requestId 字段
USER_AUTH = USER_AUTH_OB

# 获取小金比赛队伍 ID


def get_ob_team_ids(ob_sport):
    ob_team_id = [-2, -2]
    for key, value in OBDic.items():
        if value == ob_sport['mhn'].strip():
            ob_team_id[0] = key
        if value == ob_sport['man'].strip():
            ob_team_id[1] = key
    # print ('小金 比赛队伍： ' + xiaojin_i[0] + ' -> ' + xiaojin_i[1] + ' | ID: ' + str(xiaojin_team_id))
    return ob_team_id


def get_ob_rq_dx_3(ob_sport_2, ob_rq_dx, ob_type):
    ob_sport_3 = ob_sport_2['hv']
    # 全场让球分类前的正负号,生成 key
    if ob_sport_3[0] == '-':
        rq_symbol = ob_sport_3[0]
        # 全场让球分类值计算（a+b）/2,作为字典的 KEY
        rq_type = ob_sport_3[1:len(ob_sport_3)]
        if rq_type.find('/') == -1:
            rq_key = float(rq_type)
        else:
            rq_types = rq_type.split('/')
            rq_key = (float(rq_types[0]) + float(rq_types[1])) / 2.0
        # 取正负
        if rq_symbol == '-':
            rq_key *= -1
    else:
        if ob_sport_3.find('/') == -1:
            rq_key = float(ob_sport_3)
        else:
            rq_types = ob_sport_3.split('/')
            rq_key = (float(rq_types[0]) + float(rq_types[1])) / 2.0
    # 获取赔率
    ob_sport_4 = ob_sport_2['ol']
    ob_sport_5 = ob_sport_4[0]['ov']
    ob_sport_6 = ob_sport_4[1]['ov']
    rq_dx_value1 = str(round((ob_sport_5 - 100000) / 100000.0, 2))
    rq_dx_value2 = str(round((ob_sport_6 - 100000) / 100000.0, 2))
    # 添加进盘口列表
    hid = ob_sport_2['hid']
    oid1 = ob_sport_4[0]['oid']
    ot1 = ob_sport_4[0]['ot']
    oid2 = ob_sport_4[1]['oid']
    ot2 = ob_sport_4[1]['ot']
    placeNum = ob_sport_2['hn']
    ob_rq_dx[rq_key] = f"{rq_dx_value1},{rq_dx_value2},{hid},{ob_type},{oid1},{ot1},{oid2},{ot2},{placeNum}"


def get_ob_rq_dx_2(ob_sport_a, ob_type, ob_rq_dx):
    for ob_sport_i in ob_sport_a:
        if ob_sport_i['hpid'] == ob_type:
            ob_sport_1 = ob_sport_i['hl']
            # print str(ob_sport_1).replace('u', '').decode('unicode-escape')
            # 如果该数据存在
            if ob_sport_1:
                # 如果数据只是个字典
                if isinstance(ob_sport_1, dict):
                    get_ob_rq_dx_3(ob_sport_1, ob_rq_dx, ob_type)
                # 如果数据是列表，包含多个赔率
                if isinstance(ob_sport_1, list):
                    for ob_sport_2 in ob_sport_1:
                        get_ob_rq_dx_3(ob_sport_2, ob_rq_dx, ob_type)


# 获取小金比赛的全场让球、大小 ob_type= 4 (全场让球)，2（全场大小），19（半场让球），18（半场大小）
def get_ob_rq_dx(ob_sport, ob_type):
    # print (ob_sport)
    ob_rq_dx = {}
    ob_sport_a = ob_sport['hps']
    ob_sport_b = ob_sport['hpsAdd']
    get_ob_rq_dx_2(ob_sport_a, ob_type, ob_rq_dx)
    get_ob_rq_dx_2(ob_sport_b, ob_type, ob_rq_dx)
    return ob_rq_dx


class PandaBC(BaseBC):

    bc_type = "ob"
    # 请求联赛 ids
    url_mids = "https://api.lzwkbgtuq.com/yewu11/v1/w/structureTournamentMatches"
    headers_mids = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
        "Referer": "https://user-pc-bw4.4lxd71h6.com/",
        "requestId": USER_AUTH
    }
    data_post_mids = {"apiType": 1,
                      "cuid": "220087197198348288",
                      "euid": "3020101",
                      "name": "structureTournamentMatches",
                      "orpt": 0,
                      "pids": "",
                      "sort": 1,
                      "tid": ""}
    # 请求所有比赛信息
    url_games = "https://api.lzwkbgtuq.com/yewu11/v1/w/structureMatchBaseInfoByMids"
    data_post_games = {"mids": "",  # 需动态设置
                       "cuid": "220087197198348288",
                       "sort": 1, "pids": "", "euid": "3020101", "cos": 0}
    # 爬取数据

    def crawling(self):
        resp_mids = requests.post(self.url_mids, headers=self.headers_mids,
                                  data=json.dumps(self.data_post_mids), verify=False)
        print("**********************************************************************")
        data_mids = self.parseMids(resp_mids.json())
        resp_mids.close()
        print("联赛 mids = " + data_mids)
        self.data_post_games["mids"] = data_mids
        resp_games = requests.post(self.url_games, headers=self.headers_mids,
                                   data=json.dumps(self.data_post_games), verify=False)
        resp_games.close()
        return self.parse(resp_games.json())

    flag = True  # 根据 flag 决定请求前40还是后续数据
    MAX_COUNT = 40  # 第一次最多请求多少组数据
    # 解析分类 ids，用来进行比赛请求参数

    def parseMids(self, data):
        if MODE_GQ:
            midsdata = data['data']['livedata']
        else:
            midsdata = data['data']['nolivedata']
        print(f"一共获取到 {len(midsdata)} 个联赛")
        midsStr = ""
        count = 0
        start_index = 0
        if len(midsdata) > self.MAX_COUNT:
            if self.flag:
                count = self.MAX_COUNT
            else:
                count = len(midsdata)
                start_index = self.MAX_COUNT
        else:
            count = len(midsdata)
        # 取反
        self.flag = ~self.flag
        # 拼接需要请求的联赛 id
        for i in range(start_index, count):
            if midsdata[i]["tn"] == "梦幻对决":
                print(f"index:{i}, 梦幻对决 无效比赛")
                continue
            midsStr = midsStr + ',' + midsdata[i]['mids']
        print(f"拼接{start_index} -> {count} 个联赛 id")
        # for sport in midsdata:
        #     midsStr = midsStr + ',' + sport['mids']
        return midsStr.replace(",", "", 1)

    # 解析球赛数据
    def parse(self, data):
        # 先清除上次爬去的数据
        self.game_list.clear()
        ob_list = data['data']['data']
        for ob_sport in ob_list:
            sport_game = {}
            # csid = 1 代表该数据属于足球
            if ob_sport['csid'] != '1':
                continue
            # print str(ob_sport).decode('unicode-escape')
            sport_game['type'] = self.bc_type
            # 获取并转换比赛时间，格式如 2013-10-10 23:40:00 (原数据为时间戳 1642080000000)
            timeStamp = float(ob_sport['mgt'])
            timeArray = time.localtime(timeStamp / 1000.0)
            sport_game['time'] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            ob_team_id = get_ob_team_ids(ob_sport)
            sport_game['league_name'] = ob_sport['tn']
            sport_game['team_id_1'] = ob_team_id[0]
            sport_game['team_id_2'] = ob_team_id[1]
            sport_game['team_name_1'] = ob_sport['mhn'].strip()
            sport_game['team_name_2'] = ob_sport['man'].strip()
            sport_game['mid'] = ob_sport['mid']
            sport_game['tournamentId'] = ob_sport['tid']
            sport_game['tournamentLevel'] = ob_sport['tlev']
            if ob_sport['hpsData']:
                ob_sport_a = ob_sport['hpsData'][0]
                sport_game['qc_rq_list'] = get_ob_rq_dx(ob_sport_a, '4')
                sport_game['qc_dx_list'] = get_ob_rq_dx(ob_sport_a, '2')
                sport_game['bc_rq_list'] = get_ob_rq_dx(ob_sport_a, '19')
                sport_game['bc_dx_list'] = get_ob_rq_dx(ob_sport_a, '18')
            else:
                sport_game['qc_rq_list'] = {}
                sport_game['qc_dx_list'] = {}
                sport_game['bc_rq_list'] = {}
                sport_game['bc_dx_list'] = {}
            # print str(sport_game).decode('unicode-escape')
            self.game_list.append(sport_game)
        return self.game_list

    # 核实赔率是否有变动
    def check_bet(self, game, pk, bet, iszd, ratio):
        print("**********************************************************************")
        print(f"{game['type']} 平台赔率: {ratio} 核对......")
        url_market = "https://api.lzwkbgtuq.com/yewu13/v1/betOrder/queryLatestMarketInfo"
        # data_market
        self.marketId = ""
        self.matchInfoId = game['mid']
        self.oddsId = ""
        self.oddsType = ""
        self.playId = ""
        self.placeNum = ""
        bet_list = game[pk]
        for key, value in bet_list.items():
            if bet == key:
                bet_values = value.split(',')
                self.marketId = bet_values[2]
                self.playId = bet_values[3]
                self.placeNum = int(bet_values[8])
                if iszd:
                    self.oddsId = bet_values[4]
                    self.oddsType = bet_values[5]
                else:
                    self.oddsId = bet_values[6]
                    self.oddsType = bet_values[7]

        data_market = {
            "idList": [{
                "marketId": self.marketId,
                "matchInfoId": self.matchInfoId,
                "oddsId": self.oddsId,
                "oddsType": self.oddsType,
                "playId": self.playId,
                "placeNum": self.placeNum,
                "matchType": 1,
                "sportId": "1"
            }]
        }
        # print(f"注单请求参数 {data_market}")
        # 请求注单详情信息
        resp_market = requests.post(
            url_market, headers=self.headers_mids, data=json.dumps(data_market), verify=False)
        self.resp_market_json = resp_market.json()
        resp_market.close()
        # 核对最新赔率
        if self.resp_market_json["data"][0]["currentMarket"] == None:
            print(f"获取currentMarket失败，返回结果：\n{self.resp_market_json}")
            return False
        if self.resp_market_json["data"][0]["currentMarket"]["status"] != 0:
            print(f"盘口status不等于0，返回结果：\n{self.resp_market_json}")
            return False
        self.odds = self.resp_market_json["data"][0]["currentMarket"]["marketOddsList"][0]["oddsValue"]
        # print(f"注单详情返回 {resp_market_json}")
        # print(f"获取最新赔率: {self.odds}")
        hk_odds = round((self.odds - 100000) / 100000.0, 2)
        print(f"获取最新赔率hk: {hk_odds}")
        if ratio == hk_odds:
            return True
        else:
            return False
        

    # 开始下注
    def auto_bet(self, game, iszd, money):
        print("**********************************************************************")
        url_bet = "https://api.lzwkbgtuq.com/yewu13/v1/betOrder/bet"
        # data_bet
        tournamentId = game["tournamentId"]

        # 保留两位小数，不够补 0。重要：必须2位，服务器大概率是根据此字符串进行对比的
        oddFinally = "%.02f" % (round((self.odds - 100000) / 100000.0, 2))
        playName = self.resp_market_json["data"][0]["playName"]
        matchName = game["league_name"]
        if iszd:
            playOptionName_1 = game["team_name_1"]
        else:
            playOptionName_1 = game["team_name_2"]
        playOptionName_2 = self.resp_market_json["data"][0]["currentMarket"]["marketOddsList"][0]["playOptions"]
        playOptionName = f"{playOptionName_1} {playOptionName_2}"
        tournamentLevel = game["tournamentLevel"]
        data_bet = {
            "userId": "",
            "acceptOdds": 2,
            "tenantId": 1,
            "deviceType": 2,
            "currencyCode": "CNY",
            "deviceImei": "",
            "seriesOrders": [{
                "seriesSum": 1,
                "seriesType": 1,
                "seriesValues": "单关",
                "fullBet": 0,
                "orderDetailList": [{
                    "sportId": "1",
                    "matchId": self.matchInfoId,
                    "tournamentId": tournamentId,
                    "scoreBenchmark": "",
                    "betAmount": money,
                    "marketId": self.marketId,
                    "playOptionsId": self.oddsId,
                    "odds": self.odds,
                    "oddFinally": oddFinally,
                    "playName": playName,
                    "sportName": "足球",
                    "matchType": 1,
                    "matchName": matchName,
                    "playOptionName": playOptionName,
                    "playOptions": self.oddsType,
                    "marketTypeFinally": "HK",
                    "tournamentLevel": tournamentLevel,
                    "playId": self.playId,
                    "dataSource": "TX",
                    "placeNum": self.placeNum
                }]
            }]
        }
        # print(f"下注参数 {data_bet}")
        resp_bet = requests.post(
            url_bet, headers=self.headers_mids, data=json.dumps(data_bet), verify=False)
        resp_bet_json = resp_bet.json()
        resp_bet.close()
        # print(f"下注结果 {resp_bet_json}")
        if resp_bet_json["msg"] == "成功":
            return True
        else:
            print(f"返回结果: \n{resp_bet_json}")
            return False
