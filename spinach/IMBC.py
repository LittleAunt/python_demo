# -*- coding: utf-8 -*-
from tkinter.messagebox import NO
from BaseBC import BaseBC
from config import USER_TOKEN_IM, MODE_GQ
import requests
import json
import time
from dic_im import IMDic

# 获取 im 比赛队伍 ID
def get_im_team_ids(team1, team2):
    nine_team_id = [-1, -1] # 默认值不能和其他平台默认值相同
    IM_LIST = IMDic.items()

    for key, value in IM_LIST:
        if value == team1:
            nine_team_id[0] = key
        if value == team2:
            nine_team_id[1] = key
    return nine_team_id

# 获取 IM 比赛的全场让球
# 'bti'=1, 'pi'=1 全场让球
# 'bti'=1, 'pi'=2 半场让球
# 'bti'=2, 'pi'=1 全场大小
# 'bti'=2, 'pi'=2 半场大小
def get_im_qc_rq(im, bti, pi):
    # print (json.dumps(im, ensure_ascii=False))
    im_qc_rq = {}
    for im_item in im:
        if im_item['bti'] == bti and im_item['pi'] == pi:
            im_rq_list = im_item['ws']
            # 让球key取负数
            if bti == 1:
                rq_key = -1 * im_rq_list[0]['hdp']
            else:
                rq_key = im_rq_list[0]['hdp']
            rq_value = str(im_rq_list[0]['o']) + ',' + str(im_rq_list[1]['o'])
            im_qc_rq[rq_key] = rq_value
    return im_qc_rq


class IMBC(BaseBC):
    bc_type = 'im'
    # 比赛列表id获取
    im_cid_url = 'https://imsb-bvknv.utoyen.com/api/Event/GetCompetitionList'
    im_cid_body = {"CompetitionRequestGroups":[{"SportId":1,"Market":3,"EventGroupTypeIds":[]},{"SportId":1,"Market":2,"EventGroupTypeIds":[]}],"DateFrom":None,"DateTo":None,"IsCombo":False,"ProgrammeIds":[]}
    im_cid_headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "x-token": USER_TOKEN_IM,
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": f"https://imsb-bvknv.utoyen.com?languageCode=CHS&token={USER_TOKEN_IM}"
    }
    # 比赛信息获取
    im_sport_url = "https://imsb-bvknv.utoyen.com/api/Event/GetSportEvents"
    
    session = requests.session()
    session.headers = im_cid_headers
    
    def crawling(self):
        # try:
            resp_cids = self.session.post(self.im_cid_url,
                          data=json.dumps(self.im_cid_body), timeout=5, verify=False)
            print(resp_cids.text)
            print("**********************************************************************")
            data_cids = self.parseCids(resp_cids.json())
            print(data_cids)
            # im sport request body
            im_sport_body = {
                            "SportId": 1,
                            "Market": 3,
                            "BetTypeIds": [1, 2, 3],
                            "PeriodIds": [1, 2],
                            "IsCombo": False,
                            "OddsType": 2,
                            "DateFrom": None,
                            "DateTo": None,
                            "CompetitionIds": data_cids,
                            "Season": 0,
                            "MatchDay": 0,
                            "SortType": 2,
                            "ProgrammeIds": []
                            }
            resp_games = self.session.post(self.im_sport_url, 
                                    data=json.dumps(im_sport_body), timeout=7, verify=False)
            return self.parse(resp_games.json())
        # except:
        #     return None
        
    def parseCids(self, data):
        if MODE_GQ:
            im_cids_com = data['cbml'][0]['com']
        else:
            im_cids_com = data['cbml'][1]['com']
            
        print ('\n im_cids_com length: ' + str(len(im_cids_com)))
        im_cids = []
        for com in im_cids_com:
            cid = com['cid']
            im_cids.append(cid)
        return im_cids
    
    def parse(self, data):
        # 先清除上次爬去的数据
        self.game_list.clear()
        im_list = data['sel']
        for im_sport in im_list:
            print(im_sport)
            sport_game = {}
            sport_game['type'] = self.bc_type
            # 获取并转换比赛时间，格式如 2013-10-10 23:40:00 （原数据为 2022-08-29T04:30:00-04:00，因为时区问题需要再加12）
            # 先转换成 2013-10-10 23:40:00 格式时间
            time_str = im_sport['edt']
            time_str = time_str[0:19]
            time_str = time_str.replace('T', ' ')
            # 再转换成时间戳加 12 小时
            timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            timeStamp = int(time.mktime(timeArray))
            real_timeStamp = timeStamp + 43200
            # 再转 2013-10-10 23:40:00 格式时间
            timeArray = time.localtime(real_timeStamp)
            sport_game['time'] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            
            sport_game['league_name'] = im_sport['cn']
            sport_game['team_name_1'] = im_sport['htn'].strip()
            sport_game['team_name_2'] = im_sport['atn'].strip()
            im_team_id = get_im_team_ids(sport_game['team_name_1'], sport_game['team_name_2'])
            sport_game['team_id_1'] = im_team_id[0]
            sport_game['team_id_2'] = im_team_id[1]
            
            sport_game['qc_rq_list'] = get_im_qc_rq(im_sport['mls'], 1, 1)
            sport_game['qc_dx_list'] = get_im_qc_rq(im_sport['mls'], 2, 1)
            sport_game['bc_rq_list'] = get_im_qc_rq(im_sport['mls'], 1, 2)
            sport_game['bc_dx_list'] = get_im_qc_rq(im_sport['mls'], 2, 2)
            self.game_list.append(sport_game)
            print(sport_game)
        return self.game_list