class BaseBC:

    def __init__(self):
        self.game_list = []
        
    # 爬取数据
    def crawling(self):
        pass

    # 解析数据
    def parse(self, data):
        pass

    # 自动下单
    def auto_bet(self, data):
        pass


"""
    数据结构
    
    type = ""  # 平台类型
    league_name = ""  # 联赛名称
    time = "" # 比赛时间 2013-10-10 23:40:00
    team_id_1 = ""  # 前队 id
    team_id_2 = ""  # 后队 id
    team_name_1 = ""  # 前队名称
    team_name_2 = ""  # 后队名称
    qc_rq_list = ""  # 全场让球列表 {key(赔率,value1判断正负):'value1,value2'}
    qc_dx_list = ""  # 全场大小列表
    bc_rq_list = ""  # 半场让球列表
    bc_dx_list = ""  # 半场大小列表
    game_ids = ""  # 19 比赛 ID
    *************************
    19: {
        key(赔率):'value1,value2,value1_id,value2_id' id 用来进行后续下单前的赔率请求的
    }
    ****************************
    ob:
    mid: "" # 比赛 id
    tournamentId: "" # 锦标赛 id
    tournamentLevel: "" # 锦标赛 level
    {
        key(赔率):'value1,value2,marketId,marketType,oddsId1,oddsId1Type,oddsId2,oddsId2Type,placeNum' 
        id 用来进行后续下单前的赔率请求的 
        marketId 比赛中某一个盘口 id, marketType 盘口类型
        oddsId oddsIdType下注赔率对应的 id 和类型，主队、客队不同
        placeNum 在ui第几行显示
    }
"""
