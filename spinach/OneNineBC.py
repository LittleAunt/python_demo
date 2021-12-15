from BaseBC import BaseBC
from dic_nine_wb import NineDicWB
import requests


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
        if zd[9]['ZH'] == 'Home' and zd[5] != 0:   # Home 主队，Away 客队 (19 的数据有可能赔率未显示的时候为 0 )
            for kd in nine:
                if kd[9]['ZH'] == 'Away' and zd[13] == kd[13] * -1.0:
                    key = zd[13]
                    zd_value = round(zd[5] - 1.0, 2)
                    kd_value = round(kd[5] - 1.0, 2)
                    nine_rq[key] = str(zd_value) + ',' + str(kd_value)
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
                    nine_dx[key] = str(zd_value) + ',' + str(kd_value)
    return nine_dx

class OneNineBC(BaseBC):

    bc_type = "19"
    url = "https://prod20063.1x2aaa.com/api/eventlist/asia/leagues/1/prematch"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
        "session": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcklkIjozMzE4NDk1NywiZXhwaXJlZERhdGUiOjE2Mzk2NjU0NjU1MDQsImlhdCI6MTYzOTU3ODk3MX0.wswZGOLBcSpgC8_nnPWUaQaQtrH_2h1C1dH2noo-hoc",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsYW5ndWFnZUNvZGUiOiJ6aCIsImJldHRpbmdWaWV3IjoiQXNpYW4gVmlldyIsInNvcnRpbmdUeXBlSWQiOjAsImJldHRpbmdMYXlvdXQiOjIsImRpc3BsYXlUeXBlSWQiOjEsInRpbWV6b25lSWQiOjIxLCJvZGRzU3R5bGVJZCI6IiIsImFsbG93Q2hhbmdlT2RkIjowLCJpbnRUYWJFeHBhbmRlZCI6MSwiY291bnRyeUNvZGUiOiJVQSIsImN1cnJlbmN5UmF0ZSI6MC4xMTg3NTUwODUzMzUzODYsImN1cnJlbmN5UmF0ZWV1ciI6MC4xMzk1NTQyNjUwMDE2NzYsImN1c3RvbWVyTGltaXRzIjpbXSwiY3VzdG9tZXJJZCI6MzMxODQ5NTcsImV1T2Rkc0lkIjoiMSIsImtvcmVhbk9kZHNJZCI6IjEiLCJhc2lhbk9kZHNJZCI6IjEiLCJvcGVyYXRvclRva2VuIjoiWVRsbU5HWXpNVGxpWW1WbVlXRXhPRFF4Wm1VeU1tVXdNV0V5WmpNNFpqRTZOVEpoTmpVd1lqWmxNREZtTnpnNE0yTXhNV1UwTnpGbFlUa3paR1ZtWkdNeVpUTmpOVFUxTWpBeFlUSTRObU5sTURsallUY3pNbUpsWTJGbU5qVTFZekpsWVRjNE1XSmhaRFJpT1RVMllUZGlZak5tWlRBeE56azFZak14T1Rrek5ERmpaREk1TW1FMU56STJOREJqTm1RME5UaGlZMkUzWlRObE1EZG1aVEV5TlRRMk5qQmtOVEppTmpnek9Ua3haVGd5WVRNMU16TXhOMlF6TXpnMU5qRTJaR1psWWpkaU9EVmlZamcyTldKbE1UZzRNR05oTUdFM01EVTJaVGt4IiwiY3VzdG9tZXJMb2dpbiI6Ik1hbmJldHhfbXhsNjY5OSIsImN1cnJlbmN5Q29kZSI6IkNOWSIsImRvbWFpbklEIjowLCJhZ2VudElEIjoyMjYwNDA1NCwiYmFsYW5jZSI6IjAiLCJyZWFsQmFsYW5jZSI6IjAuMDAwMCIsIm1lcmNoYW50Q0MiOiIxMDU1NzMzOSIsInRlc3RDdXN0b21lciI6MCwiY3VzdG9tZXJMZXZlbCI6MCwiaWF0IjoxNjM5NTc4OTcxfQ.K-ZbHjs_z1Xr1cjNmq6moHmxGNgWDkLTlr4zvSNCCvA"
    }

    # 爬取数据
    def crawling(self):
        # 开启 charles 代理的情况下需要 verify=False，否则会报错
        resp = requests.get(self.url, headers=self.headers, verify=False) 
        return resp.json()
        
     # 解析数据
    def parse(self, data):
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
                sport_game['league_name'] = league_name
                sport_game['team_name_1'] = bs[1][0][1]['ZH'].strip()
                sport_game['team_name_2'] = bs[1][1][1]['ZH'].strip()
                nine_team_id = get_nine_team_ids(sport_game['team_name_1'], sport_game['team_name_2'])
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
