from BaseBC import BaseBC
from dic_ob import OBDic
import requests
import json

# 用户身份验证。接口中 request_headers 中的 requestId 字段
USER_AUTH = "c0e36a18b92f2ba15330574340d0666145d9cfd7"

# 获取小金比赛队伍 ID
def get_ob_team_ids(ob_sport):
    ob_team_id = [-1, -1]
    for key, value in OBDic.items():
        if value == ob_sport['mhn'].strip():
            ob_team_id[0] = key
        if value == ob_sport['man'].strip():
            ob_team_id[1] = key
    # print ('小金 比赛队伍： ' + xiaojin_i[0] + ' -> ' + xiaojin_i[1] + ' | ID: ' + str(xiaojin_team_id))
    return ob_team_id


def get_ob_rq_dx_3(ob_sport_2, ob_rq_dx):
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
    rq_dx_value = str((ob_sport_5 - 100000) / 100000.0) + ',' + str((ob_sport_6 - 100000) / 100000.0)
    # 添加进盘口列表
    ob_rq_dx[rq_key] = rq_dx_value


def get_ob_rq_dx_2(ob_sport_a, ob_type, ob_rq_dx):
    for ob_sport_i in ob_sport_a:
        if ob_sport_i['hpid'] == ob_type:
            ob_sport_1 = ob_sport_i['hl']
            # print str(ob_sport_1).replace('u', '').decode('unicode-escape')
            # 如果该数据存在
            if ob_sport_1:
                # 如果数据只是个字典
                if isinstance(ob_sport_1, dict):
                    get_ob_rq_dx_3(ob_sport_1, ob_rq_dx)
                # 如果数据是列表，包含多个赔率
                if isinstance(ob_sport_1, list):
                    for ob_sport_2 in ob_sport_1:
                        get_ob_rq_dx_3(ob_sport_2, ob_rq_dx)


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

    flag = True # 根据 flag 决定请求前40还是后续数据
    # 解析分类 ids，用来进行比赛请求参数
    def parseMids(self, data):
        nolivedata = data['data']['nolivedata']
        midsStr = ""
        count = 0
        start_index = 0
        if len(nolivedata) > 40:
            if self.flag:
                count = 40
            else:
                count = len(nolivedata)
                start_index = 40
        else:
            count = len(nolivedata)
        # 取反
        self.flag = ~self.flag
        # 拼接需要请求的联赛 id
        for i in range(start_index, count):
            midsStr = midsStr + ',' + nolivedata[i]['mids']
        print(f"请求{start_index} -> {count} 个联赛 id")
        # for sport in nolivedata:
        #     midsStr = midsStr + ',' + sport['mids']
        return midsStr.replace(",", "", 1)
    
    # 解析球赛数据
    def parse(self, data):
        # print data_json
        ob_list = data['data']['data']
        for ob_sport in ob_list:
            sport_game = {}
            # csid = 1 代表该数据属于足球
            if ob_sport['csid'] != '1':
                continue
            # print str(ob_sport).decode('unicode-escape')
            sport_game['type'] = self.bc_type
            ob_team_id = get_ob_team_ids(ob_sport)
            sport_game['team_id_1'] = ob_team_id[0]
            sport_game['team_id_2'] = ob_team_id[1]
            sport_game['team_name_1'] = ob_sport['mhn'].strip()
            sport_game['team_name_2'] = ob_sport['man'].strip()
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
