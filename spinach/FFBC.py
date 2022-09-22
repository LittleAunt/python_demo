from BaseBC import BaseBC
from dic_ff import FFDic
from config import USER_TOKEN_FF
import requests
import json
import time


def get_ff_team_ids(team1, team2):
    ff_team_id = [-3, -3]
    FF_LIST = FFDic.items()

    for key, value in FF_LIST:
        if value == team1:
            ff_team_id[0] = key
        if value == team2:
            ff_team_id[1] = key
    return ff_team_id


class FFBC(BaseBC):
    bc_type = "ff"
    ff_url = "https://gbetmxpc.tool-cheap.com/gbet/mobile/matches/commonMatches?groupId=1&gameTypeSon=&gameType=FT&showtype=RB&leagueIds=&timeStage=0&page=1&gameSort=1&dateStage=0&pageSize=200&isNovice=Y&onlyFavorite=0&extra=1"
    ff_headers = {
        "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "apiver": "4.03",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "groupid": "1",
        "tertype": "8",
        "lang": "zh-cn",
        "token": USER_TOKEN_FF,
        "wid": "1",
        "referer": "https://gbetmxpc.tool-cheap.com/inplay/FT",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    # keep-alive
    session = requests.session()
    session.headers = ff_headers

    # 爬取数据
    def crawling(self):
        try:
            resp_games = self.session.get(self.ff_url, timeout=5, verify=False)
            return self.parse(resp_games.json())
        except:
            return None

    def parse(self, data):
        print(data)
        # 先清除上次爬去的数据
        self.game_list.clear()
        ff_list = data["data"]["matchList"]["baseData"]
        for ff_game in ff_list:
            sport_game = {}
            sport_game['type'] = self.bc_type
            # 获取并转换比赛时间，格式如 2013-10-10 23:40:00 (原数据为时间戳 1642080000000)
            timeStamp = float(ff_game['gameDate'])
            timeArray = time.localtime(timeStamp / 1000.0)
            sport_game['time'] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            sport_game['league_name'] = ff_game['leagueName']
            sport_game['team_name_1'] = ff_game['homeTeam'].strip()
            sport_game['team_name_2'] = ff_game['awayTeam'].strip()
            ff_team_id = get_ff_team_ids(
                sport_game['team_name_1'], sport_game['team_name_2'])
            sport_game['team_id_1'] = ff_team_id[0]
            sport_game['team_id_2'] = ff_team_id[1]
