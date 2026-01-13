
import akshare as wb
import requests
import pandas as pd
from datetime import datetime
import math
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message=".*'T' is deprecated.*")


def CODE(code):
    code = str(code)
    if '.' in code:
        sym = code.split('.')[1]
        return sym
    else:
        sym = code
        return sym
# 获取所有股票的实时行情价格
def all_realtime_stock():
    df = wb.stock_zh_a_spot_em()
    return df
# 获取沪深京股票代码
def get_codes():
    df = wb.stock_zh_a_spot_em()
    code_list = df[["代码", "名称"]]
    return code_list

# 获取个股信息 code = "SH.6000000"
def stock_info(code):
    sym = CODE(code)
    df = wb.stock_individual_info_em(sym)
    df.columns = ["字段", "值"]
    return df

# 获取所有的个股信息，并保存在指定文件夹
def all_stock_info_save(path):
    code_list = get_codes()
    for i in range(len(code_list)):
        code = CODE(code_list.iloc[i, 0])
        df = stock_info(code)
        file = path + "\\{}.csv".format(str(code))
        df.to_csv(file, encoding="gbk")
        print("已保存:{}".format(file))

# 获取内盘外盘信息 code = "SH.6000000"
def stock_in_out(code):
    code = CODE(code)
    df = wb.stock_bid_ask_em(code)
    df_filter = df.iloc[20:36]
    df_filter.columns = ["字段", "值"]
    pd.set_option('display.float_format', '{:.2f}'.format)
    df_filter = df_filter.reset_index(drop=True)
    return df_filter

def stock_debt(code):
    code = code.lower()
    code = code.replace(".", "")
    df = wb.stock_financial_report_sina(code, "资产负债表")
    return df

def stock_profit(code):
    code = code.lower()
    code = code.replace(".", "")
    df = wb.stock_financial_report_sina(code, "利润表")
    return df

def stock_cash(code):
    code = code.lower()
    code = code.replace(".", "")
    df = wb.stock_financial_report_sina(code, "现金流量表")
    return df

def stock_pre_factor(code):
    code = code.lower()
    code = code.replace(".", "")
    df = wb.stock_zh_a_daily(symbol=code, adjust="qfq-factor")
    df.columns = ["时间", "复权比例"]
    return df

def stock_beh_factor(code):
    code = code.lower()
    code = code.replace(".", "")
    df = wb.stock_zh_a_daily(symbol=code, adjust="hfq-factor")
    df.columns = ["时间", "复权比例"]
    return df

# 获取美股实时行情数据
def mg_realtime():
    df = wb.stock_us_spot_em()
    df = df[['代码','名称','最新价','开盘价','最高价','最低价','昨收价','成交量','成交额','涨跌额','涨跌幅']]
    df['代码'] = df['代码'].str.split('.', expand=True)[1]
    return df

mg_code_list = {}
def mg_get_code(code):
    global mg_code_list
    if len(mg_code_list) < 2:
        df_codes = wb.stock_us_spot_em()
        df_codes['纯代码'] = df_codes['代码'].apply(lambda x: x.split('.')[-1])
        mg_code_list = df_codes.set_index('纯代码')['代码'].to_dict()
    return mg_code_list[code]

def mg_history_minute(code, period):
    df = wb.stock_us_hist_min_em(mg_get_code(code))
    interval = period.replace("min", "T")

    df['时间'] = df['时间'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df.set_index('时间', inplace=True)  # 将Datetime列设置为索引
    # 合成K线数据
    new_df = df.resample(interval).agg({
        '开盘': 'first',
        '最高': 'max',
        '最低': 'min',
        '收盘': 'last',
        '成交量': 'sum',
        '成交额': 'sum',
        '最新价': 'last'
    }).dropna()

    return new_df

def mg_history_daily(code, start_date, end_date, period):
    #df = stock_us_daily(code, "")
    if start_date < '2022-01-01':
        start_date = '2022-01-01'
    start_date = start_date.replace("-", "")
    end_date = end_date.replace("-", "")
    if period == "D":
        period = "daily"
    elif period == "W":
        period = "weekly"
    elif period == "M":
        period = "monthly"
    df = wb.stock_us_hist(mg_get_code(code), period, start_date, end_date, adjust="")

    #df_reset = df_filtered.reset_index(drop=True)
    return df

def mg_pre_factor(code):
    df = wb.stock_us_daily(code, "qfq-factor")
    df.columns = ["时间", "复权比例", "修正值"]
    return df

def futures_info():
    df = wb.futures_comm_info(symbol="所有")

    def insert_char(s):
        # 使用正则表达式检查字符串中是否只有三个数字字符
        if len(s) >= 3 and sum(c.isdigit() for c in s) == 3:
            # 在倒数第四个字符位置插入 '2'
            return s[:-3] + '2' + s[-3:]
        return s

    df['合约代码'] = df['合约代码'].apply(insert_char)
    return df

# 获取主力
def futures_main():
    df = wb.futures_comm_info(symbol="所有")
    df_main = df[df["备注"] == "主力合约"]
    df_main = df_main[["交易所名称", "合约名称", "合约代码"]]
    return df_main

# 商品期货的行情数据
def futures_hq_sp(code_list):
    sym = ""
    for code in code_list:
        sym = sym + code + ","
    sym = sym[:-1].upper()
    df = wb.futures_zh_spot(symbol=sym, market="CF", adjust='0')
    df["time"] = df["time"].apply(lambda x: x[:-4]+":"+x[-4:-2]+":"+x[-2:])
    df.rename(columns={'hold': 'position'}, inplace=True)
    df.columns = ['合约','时间','开盘价','最高价','最低价','最新价','买一价','卖一价','买一量','卖一量','持仓量','成交量','平均价','昨收价','结算价']
    return df

# 金融期货的行情数据
def futures_hq_jr(code_list):
    sym = ""
    for code in code_list:
        sym = sym + code + ","
    sym = sym[:-1].upper()
    df = wb.futures_zh_spot(symbol=sym, market="FF", adjust='0')
    df.rename(columns={'hold': 'position'}, inplace=True)
    df.columns = ['合约','时间','开盘价','最高价','最低价','最新价','持仓量','成交量','成交额']
    return df

def features_history(code, period):
    period = period.replace("min", "")
    df = wb.futures_zh_minute_sina(code, period)
    df.columns = ['时间','开盘价'	,'最高价','最低价','收盘价','成交量','持仓量']
    return df

def gw_futures_info(dic_page_info):

    url = "https://futsseapi.eastmoney.com/list/COMEX,NYMEX,COBOT,SGX,NYBOT,LME,MDEX,TOCOM,IPE"
    params = {
        'orderBy': 'dm',
        'sort': 'desc',
        'pageSize': '20',
        'pageIndex': '0',
        'token': '58b2fa8f54638b60b87d69b31969089c',
        'field': 'dm,sc,name',
        'blockName': 'callback',
        '_': '1705570814466'
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    total_num = data_json['total']
    total_page = math.ceil(total_num / 20) - 1
    big_df = pd.DataFrame()
    print("正在连接环境..............")
    for page in range(total_page):
        params.update({'pageIndex': page})
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json['list'])
        for dm in temp_df["dm"]:
            dic_page_info[dm] = str(page)
        big_df = pd.concat([big_df, temp_df], ignore_index=True)
    big_df.reset_index(inplace=True)
    big_df['index'] = big_df['index'] + 1
    big_df.rename(columns={
        'index': "序号",
        'dm': "代码",
        'name': "名称"
    }, inplace=True)
    big_df = big_df[[
        "序号",
        "代码",
        "名称"
    ]]

    return big_df
code_page = {}
def gw_features_info():
    global code_page
    df = gw_futures_info(code_page)
    df = df.drop('序号', axis=1)
    return df

def futures_global_em(page):

    url = "https://futsseapi.eastmoney.com/list/COMEX,NYMEX,COBOT,SGX,NYBOT,LME,MDEX,TOCOM,IPE"
    params = {
        'orderBy': 'dm',
        'sort': 'desc',
        'pageSize': '20',
        'pageIndex': '0',
        'token': '58b2fa8f54638b60b87d69b31969089c',
        'field': 'dm,sc,name,p,zsjd,zde,zdf,f152,o,h,l,zjsj,vol,wp,np,ccl',
        'blockName': 'callback',
        '_': '1705570814466'
    }
    params.update({'pageIndex': page})
    r = requests.get(url, params=params)
    data_json = r.json()
    big_df = pd.DataFrame(data_json['list'])

    big_df.reset_index(inplace=True)
    big_df['index'] = big_df['index'] + 1
    big_df.rename(columns={
        'index': "序号",
        'np': "卖盘",
        'h': "最新价",
        'dm': "代码",
        'zsjd': "-",
        'l': "最低",
        'ccl': "持仓量",
        'o': "今开",
        'p': "最高",
        'sc': "-",
        'vol': "成交量",
        'name': "名称",
        'wp': "买盘",
        'zde': "涨跌额",
        'zdf': "涨跌幅",
        'zjsj': "昨结"
    }, inplace=True)
    big_df = big_df[[
        "序号",
        "代码",
        "名称",
        "最新价",
        "涨跌额",
        "涨跌幅",
        "今开",
        "最高",
        "最低",
        "昨结",
        "成交量",
        "买盘",
        "卖盘",
        "持仓量",
    ]]
    big_df['最新价'] = pd.to_numeric(big_df['最新价'], errors="coerce")
    big_df['涨跌额'] = pd.to_numeric(big_df['涨跌额'], errors="coerce")
    big_df['涨跌幅'] = pd.to_numeric(big_df['涨跌幅'], errors="coerce")
    big_df['今开'] = pd.to_numeric(big_df['今开'], errors="coerce")
    big_df['最高'] = pd.to_numeric(big_df['最高'], errors="coerce")
    big_df['最低'] = pd.to_numeric(big_df['最低'], errors="coerce")
    big_df['昨结'] = pd.to_numeric(big_df['昨结'], errors="coerce")
    big_df['成交量'] = pd.to_numeric(big_df['成交量'], errors="coerce")
    big_df['买盘'] = pd.to_numeric(big_df['买盘'], errors="coerce")
    big_df['卖盘'] = pd.to_numeric(big_df['卖盘'], errors="coerce")
    big_df['持仓量'] = pd.to_numeric(big_df['持仓量'], errors="coerce")
    return big_df

def gw_features_realtime(code):
    global code_page
    if len(code_page) < 2:
        gw_features_info()
    df = futures_global_em(code_page[code])

    df = df[df["代码"] == code ]
    df = df.drop('序号', axis=1)
    df = df.reset_index(drop=True)
    return df


########
