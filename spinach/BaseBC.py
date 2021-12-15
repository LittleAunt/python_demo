class BaseBC:

    game_list = []

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
    team_id_1 = ""  # 前队 id
    team_id_2 = ""  # 后队 id
    team_name_1 = ""  # 前队名称
    team_name_2 = ""  # 后队名称
    qc_rq_list = ""  # 全场让球列表 {key(赔率):'value1,value2'}
    qc_dx_list = ""  # 全场大小列表
    bc_rq_list = ""  # 半场让球列表
    bc_dx_list = ""  # 半场大小列表
    game_ids = ""  # 19 比赛 ID

"""
