from BaseBC import BaseBC
from dic_nine_wb import NineDicWB
import requests
from config import USER_SESSION_19
from config import USER_AUTH_19
import json
import time


# 获取19比赛队伍 ID
def get_nine_team_ids(team1, team2):
    nine_team_id = [-1, -1]
    NINE_LIST = NineDicWB.items()

    for key, value in NINE_LIST:
        if value == team1:
            nine_team_id[0] = key
        if value == team2:
            nine_team_id[1] = key
    return nine_team_id


# 获取19比赛的让球
def get_nine_rq(nine):
    # print nine
    nine_rq = {}
    for zd in nine:
        # Home 主队，Away 客队 (19 的数据有可能赔率未显示的时候为 0 )
        if zd[9]['ZH'] == 'Home' and zd[5] != 0:
            for kd in nine:
                if kd[9]['ZH'] == 'Away' and zd[13] == kd[13] * -1.0:
                    key = zd[13]
                    zd_value = round(zd[5] - 1.0, 2)
                    kd_value = round(kd[5] - 1.0, 2)
                    nine_rq[key] = f"{zd_value},{kd_value},{zd[0]},{kd[0]}"
    return nine_rq


# 获取19比赛的大小
def get_nine_dx(nine):
    # print nine
    nine_dx = {}
    for zd in nine:
        if zd[9]['ZH'] == '大' and zd[5] != 0:
            for kd in nine:
                if kd[9]['ZH'] == '小于' and zd[13] == kd[13]:
                    key = zd[13]
                    zd_value = round(zd[5] - 1.0, 2)
                    kd_value = round(kd[5] - 1.0, 2)
                    nine_dx[key] = f"{zd_value},{kd_value},{zd[0]},{kd[0]}"
    return nine_dx


class OneNineBC(BaseBC):

    bc_type = "19"
    url = "https://prod20063.1x2aaa.com/api/eventlist/asia/leagues/1/prematch"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
        "session": USER_SESSION_19,
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "authorization": USER_AUTH_19
    }

    # 爬取数据
    def crawling(self):
        # 开启 charles 代理的情况下需要 verify=False，否则会报错
        resp = requests.get(self.url, headers=self.headers, verify=False)
        resp.close()
        return self.parse(resp.json())

     # 解析数据
    def parse(self, data):
        # 先清除上次爬去的数据
        self.game_list.clear()
        serializedData = data['serializedData']
        # 遍历联赛
        for ls in serializedData:
            # 联赛名称
            league_name = ls[1]
            # print "*******: " + league_name
            # 遍历比赛
            for bs in ls[12]:
                sport_game = {}
                sport_game['type'] = self.bc_type
                # 获取并转换比赛时间，格式如 2013-10-10 23:40:00 （原数据为 2022-01-13T12:30:00.000Z，因为时区问题需要再加8）
                # 先转换成 2013-10-10 23:40:00 格式时间
                time_str = bs[3]
                time_str = time_str.split('.')[0]
                time_str = time_str.replace('T', ' ')
                # 再转换成时间戳加 8 小时
                timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                timeStamp = int(time.mktime(timeArray))
                real_timeStamp = timeStamp + 28800
                # 再转 2013-10-10 23:40:00 格式时间
                timeArray = time.localtime(real_timeStamp)
                sport_game['time'] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                sport_game['league_name'] = league_name
                sport_game['team_name_1'] = bs[1][0][1]['ZH'].strip()
                sport_game['team_name_2'] = bs[1][1][1]['ZH'].strip()
                nine_team_id = get_nine_team_ids(
                    sport_game['team_name_1'], sport_game['team_name_2'])
                sport_game['team_id_1'] = nine_team_id[0]
                sport_game['team_id_2'] = nine_team_id[1]
                sport_game['qc_rq_list'] = {}
                sport_game['qc_dx_list'] = {}
                sport_game['bc_rq_list'] = {}
                sport_game['bc_dx_list'] = {}
                # 全场让球和大小
                for pk in bs[8][3]:
                    if pk[3][0] == 'HC0':  # 全场让球
                        sport_game['qc_rq_list'] = get_nine_rq(pk[7])
                    elif pk[3][0] == 'OU0':  # 全场大小
                        sport_game['qc_dx_list'] = get_nine_dx(pk[7])
                # 半场让球和大小
                for pk in bs[8][2]:
                    if pk[3][0] == 'HC1':  # 半场让球
                        sport_game['bc_rq_list'] = get_nine_rq(pk[7])
                    elif pk[3][0] == 'OU1':  # 半场大小
                        sport_game['bc_dx_list'] = get_nine_dx(pk[7])
                self.game_list.append(sport_game)
                # print str(sport_game).decode('unicode-escape')
        return self.game_list

    # 核实赔率是否有变动
    def check_bet(self, game, pk, bet, iszd, ratio):
        print("**********************************************************************")
        print(f"{game['type']} 平台赔率: {ratio} 核对......")
        # 获取下注详情信息
        url_bet_detail = "https://prod20063.1x2aaa.com/api/betslip/betslip"
        self.headers_bet = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
            "session": USER_SESSION_19,
            "accept": "application/json",
            "content-type": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "authorization": USER_AUTH_19,
            "referer": f"https://prod20063.1x2aaa.com/betslip/?sse=false&authorization={USER_AUTH_19}"
        }
        # 提取 selectionId，为19比赛对应赔率的 id
        self.selectionId = ""
        bet_list = game[pk]
        for key, value in bet_list.items():
            if bet == key:
                bet_values = value.split(',')
                if iszd:
                    self.selectionId = bet_values[2]
                else:
                    self.selectionId = bet_values[3]

        url_bet_detail_data = {
            "selectionId": self.selectionId,
            "viewKey": 1
        }
        url_bet_detail_data_list = []
        url_bet_detail_data_list.append(url_bet_detail_data)
        print(f"获取下注详情信息 selectionId = {self.selectionId}")
        resp_bet_detail = requests.post(url_bet_detail, headers=self.headers_bet, data=json.dumps(
            url_bet_detail_data_list), verify=False)
        resp_bet_detail.close()
        # 提取字段。判断赔率是否改变
        self.resp_json_bet = resp_bet_detail.json()
        self.trueOdds = self.resp_json_bet[0]["market"]["Changeset"]["Selection"]["TrueOdds"]
        print(f"获取最新赔率: {self.trueOdds}")
        hk_odds = round(self.trueOdds - 1.0, 2)
        print(f"获取最新赔率hk: {hk_odds}")
        if ratio == hk_odds:
            return True
        else:
            return False

    # 开始下注
    def auto_bet(self, money):
        print("**********************************************************************")
        url_stake = "https://prod20063.1x2aaa.com/api/betslip/bets"
        # data 配置
        displayOdds = self.resp_json_bet[0]["market"]["Changeset"]["Selection"]["DisplayOdds"]
        points = self.resp_json_bet[0]["market"]["Changeset"]["Selection"]["Points"]
        maxStake = round(8.4360248 * self.resp_json_bet[0]["market"]["Changeset"]
                         ["Selection"]["Settings"]["MaxWin"] / (self.trueOdds - 1), 2)
        stake = money  # 下注额*********
        potentialReturns = str(round(self.trueOdds * stake, 2))
        selectionName = self.resp_json_bet[0]["market"]["Changeset"]["Selection"]["BetslipLine"]

        data_stake = [{
            "betName": "single bet",
            "type": "single",
            "selectionsMapped": [{
                "id": self.selectionId,
                "trueOdds": self.trueOdds,
                "displayOdds": displayOdds,
                "points": points
            }],
            "trueOdds": self.trueOdds,
            "displayOdds": displayOdds,
            "clientOdds": str(self.trueOdds),
            "comboSize": 0,
            "isLive": False,
            "numberOfLines": 1,
            "maxStake": maxStake,
            "minStake": 8.44,
            "numberOfBets": 1,
            "stake": stake,
            "potentialReturns": potentialReturns,
            "oddStyleID": "1",
            "freeBet": {
                "id": 0,
                "amount": 0,
                "gainDecimal": 0
            },
            "sportID": 1,
            "metaData": {
                "device": "desktop",
                "isTablet": False,
                "bettingView": "Asian View",
                "fullURL": "https://prod20063.1x2aaa.com/zh/asian-view/today/%25E8%25B6%25B3%25E7%2590%2583",
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
            },
            "selectionsNames": [{
                "id": self.selectionId,
                "selectionName": selectionName
            }],
            "selectionsPlaced": [self.selectionId]
        }]
        # print(f"下注参数 data {data_stake}")
        resp_stake = requests.post(
            url_stake, headers=self.headers_bet, data=json.dumps(data_stake), verify=False)
        resp_stake_json = resp_stake.json()
        resp_stake.close()
        # print(f"下注结果 {resp_stake_json}")
        if resp_stake_json["status"] == "Open":
            return True
        else:
            return False
