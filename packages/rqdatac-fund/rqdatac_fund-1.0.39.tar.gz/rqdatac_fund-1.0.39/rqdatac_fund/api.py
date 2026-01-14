# -*- coding: utf-8 -*-
import datetime
import warnings
from collections import defaultdict
from functools import reduce

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api, ttl_cache
from rqdatac.services.basic import Instrument
from rqdatac.services.calendar import get_trading_dates_in_type
from rqdatac.utils import to_date, to_datetime, pd_version, is_panel_removed
from rqdatac.validators import (
    ensure_date_str,
    ensure_date_int,
    ensure_list_of_string,
    ensure_string_in,
    check_items_in_container,
    ensure_trading_date,
    ensure_date_range,
    raise_for_no_panel,
    check_type
)
from rqdatac.rqdatah_helper import rqdatah_serialize, http_conv_instruments, rqdatah_no_index_mark


def _get_instrument(order_book_id, market="cn"):
    d = _all_instruments_dict(market)
    return d.get(order_book_id)


@ttl_cache(3 * 3600)
def _all_instruments_list(market):
    il = [Instrument(i) for i in get_client().execute("fund.all_instruments", market)]
    il.sort(key=lambda i: i.order_book_id)
    return il


@ttl_cache(3 * 3600)
def _all_instruments_dict(market):
    all_list = _all_instruments_list(market)
    d = {}
    for i in all_list:
        d[i.order_book_id] = i
        d[i.symbol] = i

    return d


def ensure_fund(ob, market="cn"):
    try:
        return _all_instruments_dict(market)[ob].order_book_id
    except KeyError:
        warnings.warn("invalid order_book_id: {}".format(ob))
        return None

def ensure_obs(order_book_ids, market="cn"):
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    order_book_ids = list(set(order_book_ids))
    validated_order_book_ids = []
    for oid in order_book_ids:
        validated_oid = ensure_fund(oid, market)
        if validated_oid is not None:
            validated_order_book_ids.append(validated_oid)
    if not validated_order_book_ids:
        raise ValueError("No valid fund order book ids provided")
    return validated_order_book_ids


class MainCodeMap:
    DATE_MIN = 20010101
    relation_dict = {
        "multi_currency": 0,
        "multi_share": 1,
        "parent_and_child": 2,
    }

    def __init__(self):
        self.relations = defaultdict(list)
        self.main_code_map = {}
        self.DATE_MAX = ensure_date_int(datetime.date.today())


    def add_relation(self, order_book_id, related_ob, start_date, end_date, relation_type):
        start_date = ensure_date_int(start_date) if start_date else self.DATE_MIN
        end_date = ensure_date_int(end_date) if end_date else self.DATE_MAX
        relation_type = self.relation_dict.get(relation_type, -1)
        self.relations[order_book_id].append((related_ob, start_date, end_date, relation_type))
    

    def gen_map(self):
        for order_book_id, relations in self.relations.items():
            relations = sorted(relations, key=lambda x: x[3])
            indexs = sorted(list(set(
                # 取 relations 中的所有端点值生成 indexs
                # 这里多加了个 end+1 是因为需要考虑 ob 在转型后自己作为 main_code 的情况，需要用 fillna 填充自己的 ob
                reduce(lambda x, y: x + y, [[x[1] + 1, x[2], x[2] + 1] for x in relations])
            )))
            series = pd.Series(index=indexs)
            for related_ob, start, end, _ in relations:
                # ob 在 end 这一天还可能有数据，所以这里取到 end
                # 用 start+1 的原因是 start 可能会和其他 relation 的 end 相等
                series.loc[start + 1:end] = related_ob
            series = series.fillna(order_book_id)
            series.drop_duplicates(inplace=True, keep='first')
            self.main_code_map[order_book_id] = series
    

    def get_main_code(self, order_book_id, start_date=None, end_date=None):
        if order_book_id not in self.main_code_map:
            return [order_book_id]
        if start_date is None and end_date is None:
            return self.main_code_map[order_book_id].tolist()
        start_date = ensure_date_int(start_date)
        end_date = ensure_date_int(end_date)
        result = []
        series = self.main_code_map[order_book_id]
        # 从后往前，如果 date <= start_date，则后面无需再判断
        for date in reversed(series.index):
            if date <= start_date:
                result.append(series.loc[date])
                break
            if date <= end_date:
                result.append(series.loc[date])
        return result


@ttl_cache(3 * 3600)
def _all_main_code_map(market):
    relation_documents = get_client().execute("fund.get_related_code", None,
                                              relation_types=["multi_share", "parent_and_child", "multi_currency"],
                                              market=market)
    if not relation_documents:
        return {}
    
    map = MainCodeMap()
    for doc in relation_documents:
        map.add_relation(doc["related_id"], doc["order_book_id"], doc["effective_date"], doc["cancel_date"], doc["type"])
    map.gen_map()
    return map


def to_main_code(order_book_ids, start_date=None, end_date=None, market='cn'):
    """获取基金的主基金

    :param order_book_ids: 基金代码或者基金代码列表
    :param start_date: 开始日期，如果不指定，则返回所有时间段的主基金
    :param end_date: 结束日期，如果不指定，则返回所有时间段的主基金
    :param market:  (Default value = 'cn')
    :returns: DataFrame

    """ 
    main_code_map = _all_main_code_map(market)
    # 单天查询，需要回溯最近的有数据的一天，无法确定最近的一天在哪个区间，因此在该天之前的区间 main_code 都要返回
    if start_date == end_date and start_date is not None:
        start_date = main_code_map.DATE_MIN
    return {
        ob: main_code_map.get_main_code(ob, start_date, end_date)
        for ob in order_book_ids
    }


def main_code_flattern(main_codes):
    """把 main_code 列表平铺并去重"""
    return list(set(code for codes in main_codes.values() for code in codes))


def with_secondary_fund(main_codes, data, date_type='range'):
    """将主基金与次级基金关联的函数

    :param main_codes: 主基金代码列表
    :param data: 获取并处理好的数据，DataFrame
    :param date_type:  数据的区间类型，'range': 返回一个区间内数据，'date': 返回离某一天最近的数据
                       对于'date'类型，需要做额外处理，因为 main_codes 可能有多个，需要取返回数据中最近的那个
                       (Default value = 'range')
    :returns: DataFrame
    
    """
    if not main_codes or data is None or data.empty:
        return data
    # 把所有 main_code 都不在 data 中的 ob 过滤掉
    main_codes = {
        k: v for k,v in main_codes.items()
        if set(v) & set(data.index.levels[0])
    }
    order_book_ids = main_codes.keys()
    main_codes = main_codes.values()
    if date_type == 'date':
        main_codes = [
            # 遍历每个 ob 的 main_codes，拿到对应数据的日期，取最近的那个
            sorted(
                (data.loc[id].index.values[-1], id) for id in codes if id in data.index.levels[0]
            )[-1][1]
            for codes in main_codes 
        ]
    index_names = list(data.index.names)
    related_oid_establishment_df = pd.DataFrame({
        '_oids': order_book_ids,
        index_names[0]: main_codes,
        '_establishment_date': [ _get_instrument(oid).establishment_date for oid in order_book_ids]
    })
    related_oid_establishment_df = related_oid_establishment_df.explode(index_names[0])
    related_oid_establishment_df['_establishment_date'] = pd.to_datetime(related_oid_establishment_df['_establishment_date'], format='%Y-%m-%d')
    data.reset_index(inplace=True)
    data = data.merge(related_oid_establishment_df, how='inner', on=index_names[0])
    data = data[data[index_names[1]] >= data['_establishment_date']]
    # 对于主次基金上架日期不一致修正后，会出现空值情况，对此统一返回 None
    if data.empty:
        return
    data.drop([index_names[0], '_establishment_date'], axis=1, inplace=True)
    data.rename(columns={'_oids': index_names[0]}, inplace=True)
    data.set_index(index_names, inplace=True)
    data.sort_index(inplace=True)
    return data


@export_as_api(namespace="fund")
@rqdatah_no_index_mark
def all_instruments(date=None, market="cn"):
    """获取所有公募基金信息

    Parameters
    ----------
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，默认为当前日期。过滤掉在该日期尚未上市交易的基金合约
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 合约代码
        - symbol : str, 证券的简称
        - amc : str, 基金公司
        - fund_manager : str, 基金经理
        - establishment_date : pandas.Timestamp, 基金成立日期
        - listed_date : pandas.Timestamp, 发基金上市日
        - transition_time : str, 转型次数。'0'-原始基金，'1'-第一次转型后基金，'2'-第二次转型后基金，以此类推
        - accrued_daily : str, 货币基金收益分配方式(份额结转方式) 按日结转还是其他结转
        - de_listed_date : pandas.Timestamp, 基金退市日
        - stop_date : pandas.Timestamp, 基金终止日
        - exchange : str, 交易所，'XSHE' - 深交所, 'XSHG' - 上交所
        - benchmark : str, 业绩比较基准
        - latest_size : float, 最新基金规模（单位：元）
        - fund_type : str, 基金类型

    Examples
    --------
    >>> fund.all_instruments().head()

    0  order_book_id        listed_date     issuer         symbol   fund_type  \
    0        233001    2004-03-26  摩根士丹利华鑫基金       大摩基础行业混合      Hybrid
    1        165519    2013-08-16       信诚基金  信诚中证800医药指数分级  StockIndex
    2        004234    2017-01-19       中欧基金      中欧数据挖掘混合C      Hybrid
    3        370026    2013-02-04     上投摩根基金      上投轮动添利债券C        Bond
    4        519320    2016-05-04     浦银安盛基金   浦银安盛幸福聚利定开债A       Other

    fund_manager   latest_size                          benchmark
    0          孙海波  1.318854e+08          沪深300指数×55%+ 中证综合债券指数×45%
    1           杨旭  2.371657e+08  95%×中证800制药与生物科技指数收益率+5%×金融同业存款利率
    2           曲径           NaN       沪深300指数收益率×60%+中债综合指数收益率×40%
    3           唐瑭  8.183768e+06                           中证综合债券指数
    4          刘大巍  3.018930e+09                 一年期定期存款利率(税后)+1.4%
    """
    a = _all_instruments_list(market)
    if date is not None:
        date = ensure_date_str(date)
        a = [i for i in a if i.listed_date < date]

    df = pd.DataFrame(
        [
            [
                v.order_book_id,
                v.establishment_date,
                v.listed_date,
                v.transition_time,
                v.amc,
                v.symbol,
                v.fund_type,
                v.fund_manager,
                v.latest_size,
                v.benchmark,
                v.accrued_daily,
                v.de_listed_date,
                v.stop_date,
                v.exchange,
                v.round_lot,
            ]
            for v in a
        ],
        columns=[
            "order_book_id",
            "establishment_date",
            "listed_date",
            "transition_time",
            "amc",
            "symbol",
            "fund_type",
            "fund_manager",
            "latest_size",
            "benchmark",
            "accrued_daily",
            "de_listed_date",
            "stop_date",
            "exchange",
            "round_lot",
        ],
    )
    df = df[6 == df["order_book_id"].str.len()]
    df = df.drop_duplicates().sort_values(['order_book_id', 'listed_date'])
    return df.reset_index(drop=True)


@export_as_api(namespace="fund")
@rqdatah_serialize(converter=http_conv_instruments)
def instruments(order_book_ids, market="cn"):
    """获取基金基础信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码，例如 '000001'
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    Instrument object or list
        包含以下字段：
        - order_book_id : str, 合约代码
        - transition_time : int, 合约代码复用次数，代码从来都属于唯一个基金，则 transition_time 为零
        - symbol : str, 证券的名称
        - issuer : str, 基金公司(即将被废弃，同字段请使用`amc`)
        - fund_manager : str, 基金经理
        - establishement_date : pandas.Timestamp, 基金成立日
        - listed_date : pandas.Timestamp, 基金上市日
        - stop_date : pandas.Timestamp, 基金终止日
        - de_listed_date : pandas.Timestamp, 基金退市日
        - benchmark : str, 业绩比较基准
        - latest_size : float, 最新基金规模（单位：元）
        - abbrev_symbol : str, 基金简称
        - object : str, 投资目标
        - investment_scope : str, 投资范围
        - min_investment : str, 基金最小投资额
        - type : str, 合约的资产类型
        - fund_type : str, 基金类型
        - least_redeem : str, 最小申赎份额，仅对 ETF 展示
        - amc : str, 基金公司
        - amc_id : str, 基金公司 ID
        - accrued_daily : bool, 货币基金收益分配方式(份额结转方式) 按日结转还是其他结转
        - exchange : str, 交易所，`XSHE` - 深交所, `XSHG` - 上交所
        - round_lot : int, 一手对应多少份，通常公募基金一手是 1 份
        - trustee : int, 基金托管人代码
        - redeem_amount_days : int, 赎回款到账天数
        - confirmation_days : int, 申赎份额确认天数

    Examples
    --------
    查询某基金合约信息

    >>> fund.instruments('000014')

    Instrument(order_book_id='000014', benchmark='100.0％×一年定期存款收益率(税后)加1.2%', issuer='华夏基金管理有 限公司', establishment_date='2013-03-19', listed_date='2013-03-19', de_listed_date='0000-00-00', stop_date='0000-00-00', symbol='华夏聚利债券', fund_manager='何家琪', fund_type='Bond', accrued_daily=False, latest_size=667046240.1, type='PublicFund', transition_time=1, exchange='', amc_id='41511', amc='华夏基金管理有限公司', abbrev_symbol='华夏聚利',..., min_investment=1.0, object='在控制风险的前提下，追求较高的当期收入和总回报。', trustee=3037, redeem_amount_days=7, confirmation_days=1, round_lot=1.0)

    当某个旧基金的合约代码被重复使用，如何查找它的历史合约信息

    >>> fund.instruments('000014_CH0')

    Instrument(order_book_id='000014_CH0', benchmark='100.0％×一年定期存款收益率(税后)加1.2%', issuer='华夏基金管理有限公司', establishment_date='2013-03-19', listed_date='2013-03-19', symbol='华夏一年债', accrued_daily=False, fund_type='Bond', transition_time=0, de_listed_date='2014-03-19', stop_date='2014-03-19', latest_size=4016611053.94, type='PublicFund', exchange='', amc_id='41511', amc='华夏基金管理有限公司', round_lot=1.0)

    """
    order_book_ids = ensure_list_of_string(order_book_ids)
    if len(order_book_ids) == 1:
        return _get_instrument(order_book_ids[0])
    d = _all_instruments_dict(market)
    return [d[i] for i in order_book_ids if i in d]


NAV_FIELDS = (
    "acc_net_value",
    "unit_net_value",
    "change_rate",
    "adjusted_net_value",
    "daily_profit",
    "weekly_yield",
)


@export_as_api(namespace="fund")
def get_nav(order_book_ids, start_date=None, end_date=None, fields=None, expect_df=False, market="cn"):
    """获取基金净值信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的结束日期，start_date ,end_date 不传参数时默认返回所有数据
    fields : str | list[str], optional
        查询字段，可选字段见下方返回，默认返回所有字段
    expect_df : bool, optional
        默认为 False，返回原有的数据结构。若调为True，则返回 pandas dataframe
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - unit_net_value : float, 单位净值
        - acc_net_value : float, 累计单位净值
        - adjusted_net_value : float, 复权净值
        - change_rate : float, 涨跌幅
        - daily_profit : float, 每万元收益
        - weekly_yield : float, 7 日年化收益率

    Examples
    --------
    >>> fund.get_nav(['000003','519505'],start_date=20200910,end_date=20200917)

                          unit_net_value  acc_net_value  change_rate  adjusted_net_value  daily_profit  weekly_yield
    order_book_id datetime
    000003        2020-09-10           0.912          1.122    -0.009771            1.072268           NaN           NaN
                  2020-09-11           0.915          1.125     0.003289            1.075795           NaN           NaN
                  2020-09-14           0.915          1.125     0.000000            1.075795           NaN           NaN
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields)
        for f in fields:
            if f not in NAV_FIELDS:
                raise ValueError("invalid field: {}".format(f))
    else:
        fields = NAV_FIELDS

    result = get_client().execute(
        "fund.get_nav", order_book_ids, start_date, end_date, fields, market=market
    )
    if not result:
        return
    result = pd.DataFrame(result)
    result = result.fillna(np.nan)

    if not is_panel_removed and not expect_df:
        result = result.set_index(["datetime", "order_book_id"])
        result.reindex(columns=fields)
        result = result.to_panel()
        if len(order_book_ids) == 1:
            result = result.minor_xs(order_book_ids[0])
        if len(fields) == 1:
            return result[fields[0]]
        if len(order_book_ids) != 1 and len(fields) != 1:
            warnings.warn("Panel is removed after pandas version 0.25.0."
                          " the default value of 'expect_df' will change to True in the future.")
        return result
    else:
        result.sort_values(["order_book_id", "datetime"], inplace=True)
        result.set_index(["order_book_id", "datetime"], inplace=True)
        result.reindex(columns=fields)
        if expect_df:
            return result

        if len(order_book_ids) != 1 and len(fields) != 1:
            raise_for_no_panel()

        if len(order_book_ids) == 1:
            result.reset_index(level=0, inplace=True, drop=True)
            if len(fields) == 1:
                result = result[fields[0]]
        else:
            field = result.columns[0]
            result = result.unstack(0)[field]

        return result


@export_as_api(namespace="fund")
def get_holdings(order_book_ids, date=None, market="cn", **kwargs):
    """从指定日期回溯，获取最近的基金持仓信息。

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金合约代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的持仓数据。如不指定日期，则获取所有日期的持仓数据
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 持仓合约代码，如股票持仓、债券持仓等合约代码
        - weight : float, 持仓百分比
        - date : pandas.Timestamp, 报告期
        - release_date : pandas.Timestamp, 公告发布日
        - shares : float, 持仓股数（如股票单位：1 股，债券为 NaN）
        - market_value : float, 持仓市值（单位：元，债券为 NaN）
        - symbol : str, 持仓简称
        - type : str, 持仓资产类别大类，股票 - `Stock`，债券 - `Bond`，基金 - `Fund`，权证 - `Warrant`, 期权 - `Futures`，其他 - `Other`
        - category : str, 持仓资产类别细类 （如：category='Hshare'港股，category='Ashare'A 股均属于 type='Stock' ）

    Examples
    --------
    >>> fund.get_holdings('000001',20190930)

                   order_book_id  weight      shares  ...   type         category       symbol
    fund_id date                                          ...
    000001  2019-09-30  101564021.IB  0.0221   1000000.0  ...   Bond    CorporateBond  15华能集MTN002
    000001  2019-09-30   128016.XSHE  0.0001      4172.0  ...   Bond  ConvertibleBond         雨虹转债
    000001  2019-09-30   128022.XSHE  0.0001      6248.0  ...   Bond  ConvertibleBond         众信转债
    ...

    """
    def _remove_old_secucode(df):
        # df 包括了单个id当天的所有记录.
        # 由于基金可能发生转型, 导致 df 中 fund_id 相同, 但是 secu_code 不同的情况
        # 当出现这种情况时, 只需要保留纯数字的 secu_code
        if len(set(df["secu_code"])) > 1:
            return df[df["secu_code"].str.isdigit()]
        return df

    order_book_ids = ensure_obs(order_book_ids, market)

    if date is not None:
        date = ensure_date_int(date)
        start_date = end_date = None
        main_codes = to_main_code(order_book_ids, date, date, market)
        date_type = 'date'
    else:
        if "start_date" in kwargs and "end_date" in kwargs:
            start_date = ensure_date_int(kwargs.pop("start_date"))
            end_date = ensure_date_int(kwargs.pop("end_date"))
        elif "start_date" in kwargs or "end_date" in kwargs:
            raise ValueError('please ensure start_date and end_date exist')
        else:
            start_date = end_date = None
        main_codes = to_main_code(order_book_ids, start_date, end_date, market)
        date_type = 'range'
    main_obs = main_code_flattern(main_codes)
    if kwargs:
        raise ValueError('unknown kwargs: {}'.format(kwargs))

    df = get_client().execute("fund.get_holdings_v4", main_obs, date, start_date, end_date, market=market)
    if not df:
        return

    df = pd.DataFrame(data=df)
    fields = ["type", "weight", "shares", "market_value", "symbol"]
    if "category" in df.columns:
        fields += ["category"]
    if "region" in df.columns:
        fields += ["region"]

    df.sort_values(["fund_id", "date", "type", "order_book_id"], inplace=True)
    df.set_index(["fund_id", "date"], inplace=True)
    # backward compatibility
    if "secu_code" in df.columns:
        df = df.groupby(["fund_id", "date"], group_keys=False).apply(_remove_old_secucode)
        df.drop(columns=["secu_code"], inplace=True)
    return with_secondary_fund(main_codes, df.sort_index(), date_type=date_type)


@export_as_api(namespace="fund")
def get_split(order_book_ids, market="cn"):
    """获取基金拆分信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    market : str, optional
        (Default value = "cn")

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - ex_dividend_date : pandas.Timestamp, 除权除息日
        - split_ratio : float, 拆分折算比例，1 拆几

    Examples
    --------
    >>> fund.get_split('000246').head()

              split_ratio
    2013-11-01  1.00499349
    2013-12-02  1.00453123
    2014-01-02  1.00455316
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    data = get_client().execute("fund.get_split", order_book_ids, market=market)
    if not data:
        return
    df = pd.DataFrame(data, columns=["order_book_id", "split_ratio", "ex_dividend_date"])
    return df.set_index(["order_book_id", "ex_dividend_date"]).sort_index()


@export_as_api(namespace="fund")
def get_dividend(order_book_ids, market="cn"):
    """获取基金分红信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    market : str, optional
        (Default value = "cn")

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - ex_dividend_date : pandas.Timestamp, 除权除息日
        - book_closure_date : pandas.Timestamp, 权益登记日
        - dividend_before_tax : float, 每份税前分红
        - payable_date : pandas.Timestamp, 分红发放日

    Examples
    --------
    >>> fund.get_dividend('050116')

               book_closure_date payable_date  dividend_before_tax
    2012-01-17        2012-01-17   2012-01-19                0.002
    2013-01-16        2013-01-16   2013-01-18                0.013
    2015-01-14        2015-01-14   2015-01-16                0.028
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    data = get_client().execute("fund.get_dividend", order_book_ids, market=market)
    if not data:
        return

    df = pd.DataFrame(
        data,
        columns=["order_book_id", "book_closure_date", "payable_date", "dividend_before_tax", "ex_dividend_date"],
    )
    return df.set_index(["order_book_id", "ex_dividend_date"]).sort_index()


@export_as_api(namespace="fund")
def get_manager(order_book_ids, expect_df=True, market="cn"):
    """获取指定基金的基金经理管理信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码，str 或 list of str
    expect_df : bool, optional
        默认为True，返回 pandas dataframe。若调为 False，则返回原有的数据结构
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - name : str, 基金经理名称
        - id : str, 基金经理代码
        - days : int, 基金经理管理当前基金累计天数
        - start_date : pandas.Timestamp, 基金经理开始管理当前基金的日期
        - end_date : pandas.Timestamp, 基金经理结束管理当前基金的日期（NaT 代表任职至今）
        - return : float, 基金经理任职回报
        - title : str, 职位

    Examples
    --------
    获取单只基金的基金经理管理信息

    >>> fund.get_manager('000001')

    name days start_date end_date return title
    id
    101000229 王亚伟 1211 2001-12-18 2005-04-12 0.133084 基金经理
    101000228 田擎 605 2002-07-01 2004-02-26 0.110716 基金经理助理
    ...

    获取基金列表的基金经理管理信息

    >>> fund.get_manager(['160224', '217019'])

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    docs = get_client().execute("fund.get_manager", order_book_ids, market=market)
    if not docs:
        return

    if not expect_df and not is_panel_removed:
        data = {}
        fields = []
        for doc in docs:
            data.setdefault(doc["order_book_id"], []).append(doc)
            doc.pop('order_book_id')
            if len(fields) < len(doc.keys()):
                fields = list(doc.keys())
        array = np.full((len(fields), max([len(v) for v in data.values()]), len(order_book_ids)), None)
        for i in range(max([len(v) for v in data.values()])):
            for j, order_book_id in enumerate(order_book_ids):
                try:
                    doc = data.setdefault(order_book_id, [])[i]
                except IndexError:
                    doc = None

                for k, f in enumerate(fields):
                    v = None if doc is None else doc[f]
                    array[k, i, j] = v
        result = pd.Panel(data=array, items=fields, minor_axis=order_book_ids)
        if len(order_book_ids) == 1:
            return result.minor_xs(order_book_ids[0])
        warnings.warn("Panel is removed after pandas version 0.25.0."
                      " the default value of 'expect_df' will change to True in the future.")
        return result
    else:
        df = pd.DataFrame(docs)
        df.sort_values(["order_book_id", "start_date"], inplace=True)
        df.set_index(["order_book_id", "id"], inplace=True)
        if expect_df:
            return df
        if len(order_book_ids) == 1:
            return df.reset_index(level=0, drop=True)

        raise_for_no_panel()


@export_as_api(namespace="fund")
def get_manager_info(manager_id, fields=None, market="cn"):
    """获取基金经理背景信息

    Parameters
    ----------
    manager_id : str | list[str]
        可传入基金经理 id 或名字。名字与 id 不能同时传入
    fields : str | list[str], optional
        对应返回字段，默认为所有字段
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - id : str, 基金经理代码
        - name : str, 基金经理名称
        - gender : str, 性别
        - region : str, 出生地
        - birthdate : pandas.Timestamp, 生日
        - education : str, 学历
        - practice_date : pandas.Timestamp, 执业开始时间
        - experience_time : float, 执业年限
        - background : str, 个人简介

    Examples
    --------
    获取单个基金经理背景信息

    >>> fund.get_manager_info('101002094',fields=None)

    id chinesename gender region birthdate education practice_date  experience_time                                         background
    101002094          胡剑      男     中国      None        硕士    2006-01-01             12.8      胡剑先生，经济学硕士。曾任易方达基金管理有限公...

    获取多个基金经理背景信息

    >>> fund.get_manager_info(['101002094','101010264'],fields=None)

    id chinesename gender region birthdate education practice_date  experience_time                                         background
    101002094          胡剑      男     中国      None        硕士    2006-01-01             12.8      胡剑先生，经济学硕士。曾任易方达基金管理有限公...
    101010264          刘杰   None   None      None        硕士    2010-01-01              8.8                                               核心人员

    """
    manager_id = ensure_list_of_string(manager_id)
    # 检查manager中是否同时有人员编码或姓名
    if len(set(map(lambda x: x.isdigit(), manager_id))) > 1:
        raise ValueError("couldn't get manager_id and name at the same time")

    manager_fields = ["gender", "region", "birthdate", "education", "practice_date", "experience_time", "background"]
    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, manager_fields, "fields")
    else:
        fields = manager_fields
    result = get_client().execute("fund.get_manager_info", manager_id, fields, market=market)
    if not result:
        warnings.warn("manager_id/manager_name does not exist")
        return

    df = pd.DataFrame(result).set_index("id")
    fields.insert(0, "chinesename")
    df.sort_index(inplace=True)
    return df[fields]


@export_as_api(namespace="fund")
def get_asset_allocation(order_book_ids, date=None, market="cn"):
    """获取基金资产配置

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，查询日期和报告期去比较,回溯获取距离指定日期最近的报告期数据。如不指定日期，则获取所有日期的数据
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - datetime : pandas.Timestamp, 报告期
        - info_date : pandas.Timestamp, 公告发布日
        - stock : float, 股票占净资产比例
        - bond : float, 债券占净资产比例（由于债券通过质押式回购进行融资杠杆交易的存在，债券占比数值可能超过 100%）
        - cash : float, 现金占净资产比例
        - other : float, 其他资产占净资产比例
        - nav : float, 基金净资产（单位：元）（该字段即将被废弃，被 net_asset 替代）
        - net_asset : float, 基金净资产（单位：元）
        - total_asset : float, 基金总资产（单位：元）

    Examples
    --------
    >>> fund.get_asset_allocation('000058',date='20201231')

                  info_date   stock     bond   fund cash other nav net_asset total_asset
    order_book_id datetime
    000058       2020-12-31 2021-01-22 0.311344 0.6614 NaN 0.013306 0.015539 6.928471e+08 6.928471e+08 693971161.4
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    df = get_client().execute("fund.get_asset_allocation_v2", main_obs, date, market=market)
    if not df:
        return

    columns = [
        "order_book_id", "datetime", "info_date",
        "stock", "bond", "fund", "cash", "other", "nav", "net_asset", "total_asset"
    ]
    df = pd.DataFrame(df, columns=columns)
    df["datetime"] = pd.to_datetime(df["datetime"])
    warnings.warn("'nav' is deprecated. Please use 'net_asset' instead")
    df = df.set_index(["order_book_id", "datetime"]).sort_index()
    return with_secondary_fund(main_codes, df, date_type=date_type)


@export_as_api(namespace="fund")
def get_ratings(order_book_ids, date=None, market="cn"):
    """获取基金评级信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的数据。如不指定日期，则获取所有日期的数据
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - datetime : pandas.Timestamp, 评级日期
        - zs : float, 招商评级
        - sh3 : float, 上海证券评级三年期
        - sh5 : float, 上海证券评级五年期
        - jajx : float, 济安金信评级

    Examples
    --------
    >>> fund.get_ratings('202101')

             zs  sh3  sh5  jajx
    2009-12-31  NaN  NaN  NaN   3.0
    2010-03-31  NaN  NaN  NaN   3.0
    2010-04-30  2.0  NaN  NaN   NaN
    2010-06-30  NaN  3.0  4.0   1.0
    2010-09-30  NaN  3.0  4.0   1.0
    2010-12-31  NaN  2.0  4.0   1.0
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date is not None:
        date = ensure_date_int(date)

    df = get_client().execute("fund.get_ratings_v2", order_book_ids, date, market=market)
    if not df:
        return

    df = pd.DataFrame(df, columns=["order_book_id", "datetime", "zs", "sh3", "sh5", "jajx"])
    df.sort_values(["order_book_id", "datetime"], inplace=True)
    if date is not None:
        df.drop_duplicates(subset=['order_book_id'], keep='last', inplace=True)
    df.set_index(["order_book_id", "datetime"], inplace=True)
    df.fillna(np.nan, inplace=True)
    return df.sort_index()


@export_as_api(namespace="fund")
def get_units_change(order_book_ids, date=None, market="cn"):
    """获取基金份额变动信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的数据。如不指定日期，则获取所有日期的数据
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - datetime : pandas.Timestamp, 报告期
        - subscribe_units : float, 期间申购（单位：份）
        - redeem_units : float, 期间赎回（单位：份）
        - info_date : pandas.Timestamp, 公告日期
        - units : float, 期末总份额（单位：份）
        - net_asset : float, 期末总净资产值(单位：元)

    Examples
    --------
    >>> fund.get_units_change('001554')

                          subscribe_units  redeem_units  info_date        units    net_asset
    order_book_id datetime
    001554        2015-06-30              NaN           NaN        NaT          NaN   5000049.32
                  2015-09-30      71408891.69   37755554.39 2015-10-24  38653337.30  27630465.58
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date is not None:
        date = ensure_date_int(date)

    df = get_client().execute("fund.get_units_change_v2", order_book_ids, date, market=market)
    if not df:
        return

    df = pd.DataFrame(df)
    return df.set_index(["order_book_id", "datetime"]).sort_index()
    

@export_as_api(namespace="fund")
def get_daily_units(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取距离指定日期最近发布的基金认购赎回信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - units : float, 期末总份额（单位：份）

    Examples
    --------
    >>> fund.get_daily_units('159621',20221101,20221130)

                                units
    order_book_id datetime
    159621        2022-11-01  203434717.0
    159621        2022-11-02  197434717.0
    159621        2022-11-03  194434717.0
    ...

    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if start_date and end_date and end_date < start_date:
        raise ValueError()

    df = get_client().execute(
        "fund.get_daily_units", order_book_ids, start_date, end_date, market=market
    )
    if not df:
        return

    df = pd.DataFrame(df)
    return df.set_index(["order_book_id", "datetime"]).sort_index()


@export_as_api(namespace="fund")
def get_ex_factor(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取公募基金复权因子

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 如 '2013-01-04' (Default value = None)
    :param end_date: 如 '2014-01-04' (Default value = None)
    :param market:  (Default value = "cn")
    :returns: 如果有数据，返回一个DataFrame, 否则返回None

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if start_date and end_date and end_date < start_date:
        raise ValueError()
    data = get_client().execute("fund.get_ex_factor", order_book_ids, start_date, end_date, market=market)
    if not data:
        return

    df = pd.DataFrame(
        data,
        columns=["order_book_id", "ex_factor", "ex_cum_factor", "ex_end_date", "ex_date"]
    )
    return df.set_index(["order_book_id", "ex_date"]).sort_index()


@export_as_api(namespace="fund")
def get_industry_allocation(order_book_ids, date=None, market="cn"):
    """获取基金权益类持仓行业配置

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的数据。如不指定日期，则获取所有日期的数据
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - datetime : pandas.Timestamp, 报告期
        - standard : str, 行业划分标准
        - industry : str, 行业名称
        - weight : float, 行业占比
        - market_value : float, 现持仓市值（单位：元）

    Examples
    --------
    >>> fund.get_industry_allocation('000001',date='20200630')

                           standard          industry  weight  market_value
    order_book_id datetime
    000001        2020-06-30  CSRC_2012               金融业  0.0003  1.702350e+06
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    df = get_client().execute("fund.get_industry_allocation_v2", main_obs, date, market=market)
    if not df:
        return
    # 指定字段排序
    df = pd.DataFrame(df, columns=["standard", "industry", "weight", "market_value", "order_book_id", "datetime"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index(["order_book_id", "datetime"]).sort_index()
    return with_secondary_fund(main_codes, df, date_type=date_type)


@export_as_api(namespace="fund")
def get_indicators(order_book_ids, start_date=None, end_date=None, fields=None, rule="ricequant",
                   indicator_type="value", market="cn"):
    """获取基金衍生数据

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期
    fields : str | list[str], optional
        查询字段，可选字段见下方返回，默认返回所有字段
    rule : str, optional
        指定算法，目前仅支持 'ricequant'
    indicator_type : str, optional
        指标类别，取值 'value' 或 'rank'（默认 'value'）
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        标准版涵盖的衍生指标及频率如下，字段的组成方式为 “支持的频率_字段”，如 “日度累计收益” 字段名为 'daily_return'。货币基金仅支持部分衍生指标。
        - return : 累计收益率（支持频率：daily、w1、m1、m3、m6、y2、y1、y3、y5、total、year）
        - return_a : 累计收益率（年化）（支持频率同上）
        - benchmark_return : 基准收益率（支持频率：daily、w1、m1、m3、m6、y2、y1、y3、y5、total）
        - excess : 超额收益率（支持频率同 return）
        - excess_a : 超额收益率（年化）（支持频率同上）
        - excess_win : 超额胜率（支持频率：m3、m6、y2、y1、y3、y5、total）
        - stdev_a : 波动率（年化）（支持频率：m3、m6、y2、y1、y3、y5、total）
        - dev_downside_avg_a : 下行波动率 - 均值（年化）（支持频率同上）
        - dev_downside_rf_a : 下行波动率 - 无风险利率（年化）（支持频率同上）
        - mdd : 期间最大回撤（支持频率：m3、m6、y2、y1、y3、y5、total）
        - excess_mdd : 期间超额收益最大回撤（支持频率同上）
        - mdd_days : 最大回撤持续期（支持频率同上）
        - recovery_days : 最大回撤恢复期（支持频率同上）
        - max_drop : 最大单日跌幅（支持频率同上）
        - max_drop_period : 最大连跌期数（支持频率同上）
        - neg_return_ratio : 亏损期占比（支持频率同上）
        - kurtosis : 峰度（支持频率同上）
        - skewness : 偏度（支持频率同上）
        - tracking_error : 跟踪误差（支持频率同上）
        - var : VaR（支持频率同上）
        - alpha_a : Alpha（年化）（支持频率同上）
        - alpha_tstats : Alpha Tstat（支持频率同上）
        - beta : Beta（支持频率同上）
        - beta_downside : 下行 Beta（支持频率同上）
        - beta_upside : 上行 Beta（支持频率同上）
        - sharpe_a : Sharpe Ratio（年化）（支持频率同上）
        - inf_a : Information Ratio（年化）（支持频率同上）
        - sortino_a : Sortino Ratio（年化）（支持频率同上）
        - calmar_a : Calmar Ratio（支持频率同上）
        - timing_ratio : 择时比率（支持频率同上）
        - benchmark : 指标计算基准/排名范围

    Examples
    --------
    >>> fund.get_indicators('000001',start_date=20200601,rule='ricequant',indicator_type='value',fields=['m3_alpha_a','m6_beta','benchmark'])

                          m3_alpha_a   m6_beta benchmark
    order_book_id datetime
    000001        2020-06-01   -0.017309  0.897002   偏股型基金指数
                  2020-06-02   -0.032750  0.897575   偏股型基金指数
                  2020-06-03   -0.036943  0.897945   偏股型基金指数
    ...

    >>> fund.get_indicators('000001',start_date=20200601,rule='ricequant',indicator_type='rank',fields=['m3_alpha_a','m6_beta','benchmark'])

                         m3_alpha_a   m6_beta benchmark
    order_book_id datetime
    000001        2020-06-01   555/1116  746/1015       偏股型
                  2020-06-02   590/1116  749/1015       偏股型
                  2020-06-03   601/1117  749/1015       偏股型
    ...

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(indicator_type, ["rank", "value"], "indicator_type")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
    result = get_client().execute("fund.get_indicators", order_book_ids, start_date, end_date, fields, rule=rule,
                                  indicator_type=indicator_type, market=market)
    if not result:
        return

    df = pd.DataFrame(result).set_index(keys=["order_book_id", "datetime"])
    df.sort_index(inplace=True)

    if "update_time" in df.columns:
        df.drop(columns="update_time", inplace=True)

    if fields is not None:
        return df[fields]

    # benckmark列挪到第一位
    if 'benchmark' in df.columns:
        cols = list(df.columns.values)
        cols.remove('benchmark')
        df.reindex(columns=['benchmark'] + cols)

    return df


@export_as_api(namespace="fund")
def get_snapshot(order_book_ids, fields=None, rule="ricequant", indicator_type="value", market="cn"):
    """获取基金的最新数据

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    fields : str | list[str], optional
        查询字段，例如："last_week_return", "subscribe_status"
    rule : str, optional
        指定算法，目前仅支持 'ricequant'
    indicator_type : str, optional
        指标类别，取值 'value' 或 'rank'（默认 'value'）
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        标准版涵盖的衍生指标及频率如下，字段的组成方式为 “支持的频率_字段”，如 'daily_return'。货币基金仅支持部分衍生指标。
        - return : 累计收益率
        - return_a : 累计收益率（年化）
        - benchmark_return : 基准收益率
        - excess : 超额收益率
        - excess_a : 超额收益率（年化）
        - excess_win : 超额胜率
        - stdev_a : 波动率（年化）
        - dev_downside_avg_a : 下行波动率 - 均值（年化）
        - dev_downside_rf_a : 下行波动率 - 无风险利率（年化）
        - mdd : 期间最大回撤
        - excess_mdd : 期间超额收益最大回撤
        - mdd_days : 最大回撤持续期
        - recovery_days : 最大回撤恢复期
        - max_drop : 最大单日跌幅
        - max_drop_period : 最大连跌期数
        - neg_return_ratio : 亏损期占比
        - kurtosis : 峰度
        - skewness : 偏度
        - tracking_error : 跟踪误差
        - var : VaR
        - alpha_a : Alpha（年化）
        - alpha_tstats : Alpha Tstat
        - beta : Beta
        - beta_downside : 下行 Beta
        - beta_upside : 上行 Beta
        - sharpe_a : Sharpe Ratio（年化）
        - inf_a : Information Ratio（年化）
        - sortino_a : Sortino Ratio（年化）
        - calmar_a : Calmar Ratio
        - timing_ratio : 择时比率
        - benchmark : 指标计算基准/排名范围

    Examples
    --------
    获取基金最新衍生指标值

    >>> fund.get_snapshot('000001')

                         benchmark  daily_benchmark_return  daily_excess  daily_excess_a  ...  y5_tracking_error    y5_var year_return  year_return_a
    order_book_id datetime                                                                    ...
    000001        2021-01-27   偏股型基金指数                     0.0     -0.009129       -2.300567  ...           0.062154 -0.016652    0.038263       0.691631

    获取基金最新衍生指标排名（仅展示调用）

    >>> fund.get_snapshot('000001',indicator_type='rank')

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(indicator_type, ["value", "rank"], "indicator_type")

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")

    if indicator_type == "value":
        result = get_client().execute("fund.get_snapshot", order_book_ids, fields, rule=rule, market=market)
    elif indicator_type == "rank":
        result = get_client().execute("fund.get_snapshot_rank", order_book_ids, fields, rule=rule, market=market)
    if not result:
        return

    if rule == "ricequant":
        df = pd.DataFrame(result)
        df.rename(columns={'latest_date': 'datetime'}, inplace=True)
        df.set_index(["order_book_id", "datetime"], inplace=True)
    else:
        df = pd.DataFrame(result).set_index("order_book_id")
    df.sort_index(inplace=True)
    if fields is not None:
        return df[fields]

    # update_time是清洗生成的时间 不需要返回
    if "update_time" in df.columns:
        df.drop(columns="update_time", inplace=True)

    # benckmark列挪到第一位
    if 'benchmark' in df.columns:
        cols = list(df.columns.values)
        cols.remove('benchmark')
        df.reindex(columns=['benchmark'] + cols)

    return df


@export_as_api(namespace="fund")
def get_manager_indicators(manager_ids, start_date=None, end_date=None, fields=None,
                           asset_type="stock", manage_type="all", rule="ricequant", market="cn"):
    """获取基金经理人的衍生数据

    Parameters
    ----------
    manager_ids : str | list[str]
        基金经理代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期，start_date ,end_date 不传参数时默认返回所有数据
    fields : str | list[str], optional
        查询字段，可选字段见下方返回，默认返回所有字段
    asset_type : str, optional
        在管基金类型，默认为 stock。stock - 股票型，bond - 债券型
    manage_type : str, optional
        管理方式，默认为 all。independent - 独立管理，all - 所有参与管理
    rule : str, optional
        指定算法，目前仅支持 'ricequant'
    market : str, optional
        指定市场，目前仅有中国市场('cn')的基金经理人衍生数据

    Returns
    -------
    pandas.DataFrame
        标准版涵盖的衍生指标及频率如下，字段的组成方式为 “支持的频率_字段”，如 'daily_return'.
        - return : 累计收益率（支持频率：daily、w1、m1、m3、m6、y2、y1、y3、y5、total、year）
        - return_a : 累计收益率（年化）（支持频率同上）
        - benchmark_return : 基准收益率（支持频率：daily、w1、m1、m3、m6、y2、y1、y3、y5、total）
        - excess : 超额收益率（支持频率同 return）
        - excess_a : 超额收益率（年化）（支持频率同上）
        - excess_win : 超额胜率（支持频率：m3、m6、y2、y1、y3、y5、total）
        - stdev_a : 波动率（年化）（支持频率：m3、m6、y2、y1、y3、y5、total）
        - dev_downside_avg_a : 下行波动率 - 均值（年化）（支持频率同上）
        - dev_downside_rf_a : 下行波动率 - 无风险利率（年化）（支持频率同上）
        - mdd : 期间最大回撤（支持频率：m3、m6、y2、y1、y3、y5、total）
        - excess_mdd : 期间超额收益最大回撤（支持频率同上）
        - mdd_days : 最大回撤持续期（支持频率同上）
        - recovery_days : 最大回撤恢复期（支持频率同上）
        - max_drop : 最大单日跌幅（支持频率同上）
        - max_drop_period : 最大连跌期数（支持频率同上）
        - neg_return_ratio : 亏损期占比（支持频率同上）
        - kurtosis : 峰度（支持频率同上）
        - skewness : 偏度（支持频率同上）
        - tracking_error : 跟踪误差（支持频率同上）
        - var : VaR（支持频率同上）
        - alpha_a : Alpha（年化）（支持频率同上）
        - alpha_tstats : Alpha Tstat（支持频率同上）
        - beta : Beta（支持频率同上）
        - beta_downside : 下行 Beta（支持频率同上）
        - beta_upside : 上行 Beta（支持频率同上）
        - sharpe_a : Sharpe Ratio（年化）（支持频率同上）
        - inf_a : Information Ratio（年化）（支持频率同上）
        - sortino_a : Sortino Ratio（年化）（支持频率同上）
        - calmar_a : Calmar Ratio（支持频率同上）
        - timing_ratio : 择时比率（支持频率同上）
        - benchmark : 指标计算基准

    Examples
    --------
    >>> fund.get_manager_indicators('101000932',fields=['daily_return','total_calmar_a'],start_date='2018-02-06',end_date='2018-02-12',manage_type='independent',asset_type='stock')

                       daily_return  total_calmar_a
    manager_id datetime
    101000932  2018-02-06     -0.031451        0.006801
    101000932  2018-02-07     -0.021206        0.006622
    101000932  2018-02-08      0.006771        0.006667
    101000932  2018-02-09     -0.028918        0.006426
    101000932  2018-02-12      0.027701        0.006639
    """
    manager_ids = ensure_list_of_string(manager_ids)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(asset_type, ["stock", "bond"], "asset_type")
    check_items_in_container(manage_type, ["all", "independent"], "manage_type")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
    result = get_client().execute("fund.get_manager_indicators", manager_ids, start_date, end_date, fields,
                                  asset_type=asset_type, manage_type=manage_type, rule=rule, market=market)
    if not result:
        return

    df = pd.DataFrame(result).set_index(keys=["manager_id", "datetime"])
    df.sort_index(inplace=True)
    if fields is not None:
        return df[fields]
    return df


@export_as_api(namespace="fund")
@rqdatah_no_index_mark
def get_related_code(order_book_ids, market="cn"):
    """获取分级基金的分级关系

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    market : str, optional
        指定市场，目前仅有中国市场('cn')的分级基金数据

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - main_code : str, 平级关系或母子关系的主代码
        - related_code : str, 平级关系或母子关系的次代码
        - type : str, 分级基金关系：同一基金分级关系 - multi_share， 母子基金分级关系 - parent_and_child， 同一基金不同货币关系（QDII）- multi_currency
        - effective_date : pandas.Timestamp, 该条记录的有效起始日
        - cancel_date : pandas.Timestamp, 该条记录的失效日

    Examples
    --------
    >>> fund.get_related_code(['000003','000004','005929','160513'])

      main_code related_code              type effective_date cancel_date
    0    000003       000004       multi_share     2013-02-20         NaT
    1    005929       005930       multi_share     2018-10-12  2019-01-16
    2    160513       160514       multi_share     2014-06-10         NaT
    3    160513       160514  parent_and_child     2011-05-20  2014-06-10
    4    160513       150043  parent_and_child     2011-05-20  2014-06-10

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    result = get_client().execute("fund.get_related_code", order_book_ids, market=market)
    if not result:
        return
    df = pd.DataFrame(result, columns=["order_book_id", "related_id", "type", "effective_date", "cancel_date"])
    df.rename(columns={"order_book_id": "main_code", "related_id": "related_code"}, inplace=True)
    return df


@export_as_api(namespace="fund")
def get_etf_components(order_book_ids, trading_date=None, market="cn"):
    """获取 ETF 申赎清单

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    trading_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        交易日期，默认为当天
    market : str, optional
        (Default value = "cn")

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - trading_date : pandas.Timestamp, 持仓日期
        - stock_amount : float, 股票数量
        - cash_substitute : str, 现金替代规则
        - cash_substitute_proportion : float, 现金替代比例
        - fixed_cash_substitute : float, 固定现金金额（上交所字段，深交所是用申购替换金额填充该字段）
        - redeem_cash_substitute : float, 赎回替代金额(元)（深交所）

    Examples
    --------
    >>> fund.get_etf_components('510050.XSHG', trading_date=20190117)

     trading_date  order_book_id  stock_code  stock_amount  cash_substitute  cash_substitute_proportion  fixed_cash_substitute
    0  2019-01-17  510050.XSHG    600000      5600.0              允许                               0.1    NaN
    1  2019-01-17  510050.XSHG    600016      11900.0            允许                               0.1    NaN
    2  2019-01-17  510050.XSHG    600019      4300.0              允许                               0.1    NaN
    ...
    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    ids_with_suffix = []
    for order_book_id in order_book_ids:
        if order_book_id.endswith(".XSHG") or order_book_id.endswith(".XSHE"):
            ids_with_suffix.append(order_book_id)
        elif order_book_id.startswith("1"):
            ids_with_suffix.append(order_book_id + ".XSHE")
        elif order_book_id.startswith("5"):
            ids_with_suffix.append(order_book_id + ".XSHG")
    if not ids_with_suffix:
        return

    if trading_date is not None:
        trading_date = to_date(trading_date)
        if trading_date > datetime.date.today():
            return
    else:
        trading_date = datetime.date.today()
    trading_date = ensure_date_int(ensure_trading_date(trading_date))

    result = get_client().execute("fund.get_etf_components_v2", ids_with_suffix, trading_date, market=market)
    if not result:
        return

    columns = ["trading_date", "order_book_id", "stock_code", "stock_amount", "cash_substitute",
               "cash_substitute_proportion", "fixed_cash_substitute", "redeem_cash_substitute"]
    df = pd.DataFrame(result, columns=columns)
    df.sort_values(by=["order_book_id", "trading_date", "stock_code"], inplace=True)
    df.set_index(["order_book_id", "trading_date"], inplace=True)
    return df.sort_index()


@export_as_api(namespace="fund")
def get_stock_change(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金报告期内重大股票持仓变动情况

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的开始日期，默认为最新一期数据
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的结束日期，默认为最新一期数据
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 股票合约代码
        - date : pandas.Timestamp, 持仓披露日期
        - weight : float, 持仓百分比
        - market_value : float, 持仓市值
        - change_type : str, 变动类型。1-买入，2-卖出

    Examples
    --------
    >>> fund.get_stock_change('519933','20190101','20191001')

           order_book_id  market_value  weight  change_type
    date
    2019-06-30   000921.XSHE     361296.00  0.0497            2
    2019-06-30   601288.XSHG     744548.00  0.1025            2
    ...

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_stock_change_v2", main_obs, start_date, end_date, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df = df.set_index(["fund_id", "date"]).sort_index()
    df = df[['order_book_id', 'market_value', 'weight', 'change_type']]
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_term_to_maturity(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取货币型基金的持仓剩余期限

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的开始日期，默认为最新一期数据
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的结束日期，默认为最新一期数据
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 报告期
        - term : str, 剩余期限范围
        - weight : float, 剩余期限占资产净值比例

    Examples
    --------
    >>> fund.get_term_to_maturity('050003','20190101','20191120')

               term  weight
    date
    2019-03-31     0_30  0.5013
    2019-03-31    30_60  0.1077
    2019-03-31    60_90  0.1419
    ...

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_term_to_maturity", main_obs, start_date, end_date, market=market)
    if result:
        result = [i for i in result if i is not None]
    if not result:
        return
    df = pd.DataFrame(result)
    df = df[['order_book_id', 'date', '0_30', '30_60', '60_90', '90_120', '120_397', '90_180', '>180']]
    df.set_index(['order_book_id', 'date'], inplace=True)
    df = df.stack().reset_index()
    if pd_version >= "0.21":
        df = df.set_axis(['order_book_id', 'date', 'term', 'weight'], axis=1, copy=False)
    else:
        df.set_axis(1, ['order_book_id', 'date', 'term', 'weight'])
    df = df.set_index(['order_book_id', 'date']).sort_index()
    df.dropna(inplace=True)
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_bond_stru(order_book_ids, date=None, market="cn"):
    """获取基金持仓中债券组合结构信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的债券组合结构数据。如不指定日期，则获取所有日期的债券组合结构数据
    market : str, optional
        指定市场，目前仅有中国市场('cn')的基金数据

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 基金合约代码
        - date : pandas.Timestamp, 持仓披露日期
        - bond_type : str, 债券种类：国债 - `government`，金融债券 - `financial`，企业债券 - `corporate`，可转换债券 - `convertible`，央行票据 - `bank_notes`，短期融资券 - `short_financing`，中期票据 - `medium_notes`，同业存单 - `ncd`，中小企业私募债 - `s_m_private`，地方政府债券 - `local_government`，其他债券 - `other_bond`
        - weight_nv : float, 持仓占资产净值百分比
        - weight_bond_mv : float, 持仓占债券组合市值百分比
        - market_value : float, 持仓市值（单位：元）

    Examples
    --------
    >>> fund.get_bond_structure(['000014','000005'],20200630)

                             bond_type  weight_nv  weight_bond_mv  market_value
    order_book_id date
    000005        2020-06-30     financial     0.2370        0.183999   13469400.00
                  2020-06-30   convertible     0.0347        0.026921    1970729.00
                  2020-06-30     corporate     0.3668        0.284768   20846100.00
    000014        2020-06-30    government     0.1423        0.127257   14705500.00
                  2020-06-30   convertible     0.7407        0.662522   76559552.12
                  2020-06-30     corporate     0.2350        0.210221   24292667.20
    ...

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    data = get_client().execute("fund.get_bond_stru_v2", main_obs, date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    df = df[['bond_type', 'weight_nv', 'weight_bond_mv', 'market_value']]
    return with_secondary_fund(main_codes, df, date_type=date_type)


export_as_api(get_bond_stru, namespace='fund', name='get_bond_structure')

AMC_FIELDS = ["amc_id", "amc", "establishment_date", "reg_capital"]


@export_as_api(namespace="fund")
def get_amc(amc_ids=None, fields=None, market="cn"):
    """获取基金公司详情信息

    :param amc_ids: 基金公司id或简称，默认为 None
    :param fields: 可选参数。默认为所有字段。 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    if fields is None:
        fields = AMC_FIELDS
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, AMC_FIELDS, "fields")

    result = get_client().execute("fund.get_amc", market=market)
    if amc_ids:
        amc_ids = ensure_list_of_string(amc_ids)
        amcs = tuple(amc_ids)
        result = [i for i in result if i["amc_id"] in amc_ids or i["amc"].startswith(amcs)]

    if not result:
        return
    return pd.DataFrame(result)[fields]


@export_as_api(namespace="fund")
def get_credit_quality(order_book_ids, date=None, market="cn"):
    """获取基金债券持仓投资信用评级信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询日期，回溯获取距离指定日期最近的债券投资信用评级数据。如不指定日期，则获取所有日期的债券投资评级数据
    market : str, optional
        指定市场，目前仅有中国市场('cn')的基金数据

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 持仓披露日期
        - credit_rating : str, 债券信用等级
        - bond_sector_rating_type : str, 债券持仓评级类别
        - market_value : float, 持仓市值（单位：元）

    Examples
    --------
    从指定日期回溯，获取最近的基金债券投资信用评级信息。

    >>> fund.get_credit_quality(['000003','000033'],20200620)

                         credit_rating bond_sector_rating_type  market_value
    order_book_id date
    000003        2019-12-31           未评级                债券短期信用评级  6.721030e+06
                  2019-12-31           AAA                债券长期信用评级  1.083061e+08
                  2019-12-31         AAA以下                债券长期信用评级  4.014485e+07
    000033        2019-12-31           A-1                债券短期信用评级  8.182628e+07
                  2019-12-31           未评级                债券短期信用评级  3.466683e+08
                  2019-12-31           AAA                债券长期信用评级  4.052186e+09
                  2019-12-31         AAA以下                债券长期信用评级  1.284435e+09
                  2019-12-31           AAA           资产支持证券将长期信用评级  2.036309e+07
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_credit_quality", main_obs, date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df.rename(columns={"t_type": "bond_sector_rating_type"}, inplace=True)
    df.sort_values(["order_book_id", "date", "bond_sector_rating_type", "credit_rating"], inplace=True)
    df.set_index(["order_book_id", "date"], inplace=True)
    return with_secondary_fund(main_codes, df.sort_index(), date_type=date_type)


@export_as_api(namespace="fund")
def get_irr_sensitivity(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金利率风险敏感性分析数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期, 如'2013-01-04'
    :param end_date: 结束日期, 如'2014-01-04'；在 start_date 和 end_date 都不指定的情况下，默认为最近6个月
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    start_date, end_date = ensure_date_range(start_date, end_date, delta=relativedelta(months=6))
    result = get_client().execute("fund.get_irr_sensitivity_v2", order_book_ids, start_date, end_date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


@export_as_api(namespace="fund")
def get_etf_cash_components(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取 ETF 现金差额数据

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期，start_date ,end_date 不传参数时默认返回所有数据
    market : str, optional
        (Default value = "cn")

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 预估日期
        - pre_date : pandas.Timestamp, 交易日期
        - cash_component : float, 现金差额（单位:元）
        - nav_per_basket : float, 最小申购赎回单位资产净值（单位:元）
        - est_cash_component : float, 预估现金差额（单位:元）
        - max_cash_ratio : float, 现金替代上限
        - unit_subscribe_redeem : float, 最小申赎单位（份）

    Examples
    --------
    获取单个 ETF 现金差额数据

    >>> fund.get_etf_cash_components('510050.XSHG','20191201','20191205')

    order_book_id date cash_component est_cash_component max_cash_ratio nav_per_basket pre_date
    510050.XSHG 2019-12-02 55959.24 31237.24 0.5 2646969.24 2019-11-29
    510050.XSHG 2019-12-03 31488.64 35832.64 0.5 2608899.64 2019-12-02
    ...

    获取多个 ETF 现金差额数据

    >>> fund.get_etf_cash_components(['510050.XSHG','510300.XSHG'],'20191201','20191205')

    order_book_id date cash_component est_cash_component max_cash_ratio nav_per_basket pre_date
    510050.XSHG 2019-12-02 55959.24 31237.24 0.5 2646969.24 2019-11-29
    510300.XSHG 2019-12-02 -34311.25 -29329.25 0.5 3501800.75 2019-11-29
    ...
    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)

    # 用户可能传入不带后缀的id, 这里统一处理成带后缀的id.
    for indx in range(len(order_book_ids)):
        if order_book_ids[indx].endswith(".XSHG") or order_book_ids[indx].endswith(".XSHE"):
            pass
        elif order_book_ids[indx].startswith("1"):
            order_book_ids[indx] = order_book_ids[indx] + ".XSHE"
        elif order_book_ids[indx].startswith("5"):
            order_book_ids[indx] = order_book_ids[indx] + ".XSHG"
        else:
            pass

    if end_date is None:
        end_date = datetime.date.today()
    end_date = ensure_date_int(end_date)

    if start_date is not None:
        start_date = ensure_date_int(start_date)

    result = get_client().execute(
        "fund.get_etf_cash_components", order_book_ids, start_date, end_date, market=market
    )
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return df


AMC_TYPES = ['total', 'equity', 'hybrid', 'bond', 'monetary', 'shortbond', 'qdii']


@export_as_api(namespace="fund")
def get_amc_rank(amc_ids, date=None, type=None, market="cn"):
    """获取基金公司排名

    :param amc_ids: 基金公司代码，str or list
    :param date: 规模截止时间
    :param type: 基金类型，str or list
    :param market: (Default value = "cn")
    :return: DataFrame
    """
    amc_ids = ensure_list_of_string(amc_ids)
    if date:
        date = ensure_date_int(date)
    if type is not None:
        type = ensure_list_of_string(type)
        check_items_in_container(type, AMC_TYPES, "type")

    result = get_client().execute("fund.get_amc_rank", amc_ids, date, type, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df = df.set_index(keys=['amc_id', 'type'])
    df.sort_values('date', inplace=True)
    return df


@export_as_api(namespace="fund")
def get_holder_structure(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金持有人结构

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期, start_date ,end_date 不传参数时默认返回所有数据
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 报告期
        - info_date : pandas.Timestamp, 公告日期
        - instl : float, 机构投资者持有份额(份)
        - instl_weight : float, 构投资者持有份额占比(%)
        - retail : float, 个人投资者持有份额(份)
        - retail_weight : float, 个人投资者持有份额占比(%)

    Examples
    --------
    >>> fund.get_holder_structure('000001','20190101','20200101')

                instl instl_weight retail retail_weight
    order_book_id date
    000001 2019-06-30 16995587.39 0.40 4.277759e+09 99.60
    2019-12-31 18827745.40 0.45 4.142996e+09 99.55
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if end_date is not None:
        end_date = ensure_date_int(end_date)

    if start_date is not None:
        start_date = ensure_date_int(start_date)

    result = get_client().execute(
        "fund.get_holder_structure", order_book_ids, start_date, end_date, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace="fund")
def get_qdii_scope(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取QDII地区配置

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期，start_date ,end_date 不传参数时默认返回所有数据
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 报告期
        - region : str, 地区
        - market_value : float, 市值(元)
        - weight : float, 占净资产比列

    Examples
    --------
    >>> fund.get_qdii_scope('183001','20190101','20200101')

    region market_value weight
    order_book_id date
    183001 2019-03-31 中国香港 12540825.98 20.00
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_qdii_scope", main_obs, start_date, end_date, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_benchmark(order_book_ids, market="cn"):
    """获取基金基准

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - start_date : pandas.Timestamp, 起始日
        - end_date : pandas.Timestamp, 截止日
        - index_code : str, 指数代码
        - index_name : str, 指数名称
        - index_weight : float, 指数权重

    Examples
    --------
    >>> fund.get_benchmark('000006')

    end_date index_code index_name index_weight
    order_book_id start_date
    000006 2019-02-15 2019-12-25 000905.XSHG 中证小盘500指数 0.75
    2019-02-15 2019-12-25 B00009 活期存款利率(税后) 0.25
    2019-12-25 NaT 000905.XSHG 中证小盘500指数 0.75
    2019-12-25 NaT B00009 活期存款利率(税后) 0.25
    """
    order_book_ids = ensure_obs(order_book_ids, market)

    result = get_client().execute(
        "fund.get_benchmark", order_book_ids, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "start_date"])
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='fund')
def get_instrument_category(order_book_ids, date=None, category_type=None, source='gildata', market="cn"):
    """获取合约所属风格分类

    Parameters
    ----------
    order_book_ids : str | list[str]
        单个合约字符串或合约列表，如 '000001' 或 ['000001', '000003']
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        日期，默认为最新
    category_type : str | list[str], optional
        可传入list，不指定则返回全部。可选：value - 价值风格，size - 规模风格，operating_style - 操作风格，
        duration - 久期分布，bond_type - 券种配置，industry_citics - 基金行业板块，concept - 基金概念板块，
        investment_style - 基金投资风格，universe - 基金属性，structured_fund - 分级基金标签，fund_type - 基金分类
    source : str, optional
        分类来源。gildata: 聚源
    market : str, optional
        指定市场，目前仅支持中国市场('cn')

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - category_type : str, 分类类型
        - category_index : str, 基金细分分类指数代码
        - category : str, 基金细分分类名称
        - first_type_code : str, 一级分类代码 （仅限 category_type='fund_type' ）
        - first_type : str, 一级分类名称 （仅限 category_type='fund_type' ）
        - second_type_code : str, 二级分类代码 （仅限 category_type='fund_type' ）
        - second_type : str, 二级分类名称 （仅限 category_type='fund_type' ）
        - third_type_code : str, 三级分类代码 （仅限 category_type='fund_type' ）
        - third_type : str, 三级分类名称 （仅限 category_type='fund_type' ）

    Examples
    --------
    不指定 category_type，获取 000001 默认分类类型数据

    >>> fund.get_instrument_category('000001')

                                category  category_index
    order_book_id category_type
    000001        value               blend         1014002
                  operating_style  flexible         1015003
                  size              mid_cap         1013002

    指定获取基金的基金属性、概念板块

    >>> fund.get_instrument_category('000001',category_type=['universe','concept'])

    ...
    """

    order_book_ids = ensure_obs(order_book_ids, market)

    if date:
        date = ensure_date_int(date)

    category_types = {
        'value', 'size', 'operating_style', 'duration', 'bond_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    base_category_types = category_types.copy()
    base_category_types.add("fund_type")

    if category_type is None:
        category_type = category_types
    category_type = ensure_list_of_string(category_type)

    if 1 < len(category_type) and "fund_type" in category_type:
        raise ValueError("'fund_type' can only be searched independently.")

    check_items_in_container(category_type, base_category_types, 'category_type')

    source = ensure_string_in(source, {'gildata'}, 'source')

    result = get_client().execute('fund.get_instrument_category', order_book_ids, date, category_type, source,
                                  market=market)

    if not result:
        return

    if "fund_type" in category_type:
        c = [
            "order_book_id", "category_type", "first_type_code", "first_type", "second_type_code", "second_type",
            "third_type_code", "third_type"
        ]
        df = pd.DataFrame.from_records(result, index=['order_book_id', 'category_type'], columns=c)
    else:
        df = pd.DataFrame.from_records(result, index=['order_book_id', 'category_type'])
    return df


@export_as_api(namespace='fund')
def get_category(category, date=None, source='gildata', market='cn'):
    """获取指定分类下所属基金列表

    Parameters
    ----------
    category : dict
        以 dict 的形式输入：支持输入多个 category_type、category。
        结构为{"category_type":["category"],"category_type":["category"]} ,可参考范例帮助理解。
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        默认最新日期
    source : str, optional
        分类来源，目前仅支持 'gildata' 聚源分类
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    list[str]
        返回 order_book_id 列表

    Examples
    --------
    >>> fund.get_category(category={"concept": ["人工智能","MSCI概念"], "size": "large","operating_style":"flexible"})

    ['040001', '202005', '270021', ...]
    """

    category_keys = {
        'value', 'size', 'operating_style', 'duration', 'bond_type', 'fund_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    if date:
        date = ensure_date_int(date)

    check_type(category, dict, "category")
    source = ensure_string_in(source, {'gildata'}, 'source')

    check_items_in_container(category, category_keys, 'category')
    for k in category:
        category[k] = ensure_list_of_string(category[k])

    category_types_map = defaultdict(list)

    category_type_copy = list(category.keys())
    if "fund_type" in category_type_copy:
        fund_type_df = get_category_mapping(category_type="fund_type")
        category_types_map["fund_type"].extend(fund_type_df.values.flatten().tolist())
        category_type_copy.remove("fund_type")

    if category_type_copy:
        df = get_category_mapping(category_type=category_type_copy)
        unique_index = df.index.unique()
        for idx in unique_index:
            category_types_map[idx].extend([_ for _ in df.loc[idx].values.flatten() if _ is not None])

    for c in category:
        if not set(category[c]).issubset(set(category_types_map[c])):
            raise ValueError("Unexpected category.")
    return get_client().execute('fund.get_category_v2', category, date, source, market=market)


@export_as_api(namespace='fund')
def get_category_mapping(source='gildata', category_type=None, market="cn"):
    """获取风格分类列表概览

    Parameters
    ----------
    source : str, optional
        分类来源。gildata: 聚源
    category_type : str | list[str], optional
        风格类型, 默认返回除 fund_type 以外的风格
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - category_type : str, 分类类型
        - category : str, 分类名称 或 first_type/second_type/... 当 category_type='fund_type' 时
        - category_index : str, 基金细分分类指数代码
        - first_type_code : str, 一级分类代码 （仅限 category_type='fund_type' ）
        - first_type : str, 一级分类名称 （仅限 category_type='fund_type' ）
        - second_type_code : str, 二级分类代码 （仅限 category_type='fund_type' ）
        - second_type : str, 二级分类名称 （仅限 category_type='fund_type' ）
        - third_type_code : str, 三级分类代码 （仅限 category_type='fund_type' ）
        - third_type : str, 三级分类名称 （仅限 category_type='fund_type' ）

    Examples
    --------
    >>> fund.get_category_mapping()

    category category_index
    category_type
    structured_fund   structured_fund           None
    universe              fund_of_etf           None
    ...
    """

    source = ensure_string_in(source, {'gildata'}, 'source')

    # 参数category_type为None时默认取除fund_type以外的风格, 因为fund_type不能和其他风格共存
    category_types = {
        'value', 'size', 'operating_style', 'duration', 'bond_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    if category_type is None:
        category_type = category_types
    category_type = ensure_list_of_string(category_type)

    if "fund_type" in category_type:
        assert len(category_type) == 1, "'fund_type' can only be searched independently."
    else:
        check_items_in_container(category_type, category_types, 'category_type')

    result = get_client().execute("fund.get_category_mapping", source, market=market)
    if not result:
        return
    if "fund_type" in category_type:
        columns = [
            "first_type_code", "first_type", "second_type_code", "second_type", "third_type_code", "third_type",
            "category_type"
        ]
        df = pd.DataFrame(result, columns=columns)
        df = df["fund_type" == df["category_type"]]
    else:
        columns = ["category", "category_index", "category_type"]
        df = pd.DataFrame(result, columns=columns)
        df = df[df["category_type"].isin(category_type)]

    df.set_index(keys=["category_type"], inplace=True)
    return df


@export_as_api(namespace="fund")
def get_benchmark_price(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金 benchmark 价格

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金order_book_id, str or list
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期，不指定则不限制开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期，不指定则不限制结束日期
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - date : pandas.Timestamp, 交易日期
        - close : float, 收盘价

    Examples
    --------
    >>> fund.get_benchmark_price('1015003',start_date=20200520,end_date=20200526)

                              close
    order_book_id date
    1015003       2020-05-20  1650.3720
                  2020-05-21  1631.6981
                  2020-05-22  1598.8213
                  2020-05-25  1597.9072

    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    result = get_client().execute(
        "fund.get_benchmark_price", order_book_ids, start_date, end_date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


FINANCIALS_FIELDS = [
    'accts_payable',
    'accts_receivable',
    'cash_equivalent',
    'deferred_expense',
    'deferred_income_tax_assets',
    'deferred_income_tax_liabilities',
    'dividend_receivable',
    'financial_asset_held_for_trading',
    'financial_liabilities',
    'interest_payable',
    'interest_receivable',
    'leverage',
    'management_fee_payable',
    'other_accts_payable',
    'other_accts_receivable',
    'other_assets',
    'other_equity',
    'other_liabilities',
    'paid_in_capital',
    'profit_payable',
    'redemption_fee_payable',
    'redemption_money_payable',
    'sales_fee_payable',
    'stock_cost',
    'stock_income',
    'tax_payable',
    'total_asset',
    'total_equity',
    'total_equity_and_liabilities',
    'total_liabilities',
    'transaction_fee_payable',
    'trust_fee_payable',
    'undistributed_profit',
    'info_date'
]


@export_as_api(namespace="fund")
def get_financials(order_book_ids, start_date=None, end_date=None, fields=None, market="cn"):
    """获取基金财务信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期，start_date ,end_date 不传参数时默认返回所有数据
    fields : str | list[str], optional
        查询字段，可选字段见下方返回，默认返回所有字段
    market : str, optional
        默认是中国内地市场('cn') 。

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - cash_equivalent : float, 现金及现金等价物
        - financial_asset_held_for_trading : float, 交易性金融资产
        - dividend_receivable : float, 应收股利
        - interest_receivable : float, 应收利息
        - deferred_income_tax_assets : float, 递延所得税资产
        - other_accts_receivable : float, 其他应收账款
        - accts_receivable : float, 应收账款
        - other_assets : float, 其他资产
        - deferred_expense : float, 待摊费用
        - total_asset : float, 总资产
        - financial_liabilities : float, 交易性金融负债
        - redemption_money_payable : float, 应付赎回款
        - redemption_fee_payable : float, 应付赎回费
        - management_fee_payable : float, 应付管理人报酬
        - trust_fee_payable : float, 应付托管费
        - sales_fee_payable : float, 应付销售服务费
        - transaction_fee_payable : float, 应付交易费用
        - tax_payable : float, 应交税费
        - interest_payable : float, 应付利息
        - profit_payable : float, 应付利润
        - deferred_income_tax_liabilities : float, 递延所得税负债
        - accts_payable : float, 应付帐款
        - other_accts_payable : float, 其他应付款
        - other_liabilities : float, 其他负债
        - total_liabilities : float, 负债合计
        - paid_in_capital : float, 实收基金
        - undistributed_profit : float, 未分配利润
        - other_equity : float, 其他权益
        - total_equity : float, 总权益
        - total_equity_and_liabilities : float, 负债和所有者权益合计
        - leverage : float, 杠杆率
        - stock_cost : float, 股票买入成本
        - stock_income : float, 股票买入收入
        - info_date : pandas.Timestamp, 报告/公告日期

    Examples
    --------
    >>> fund.get_financials('000001','20190101','20191231',fields=['total_asset','total_equity','leverage','stock_cost','stock_income'])

    leverage stock_cost stock_income total_asset total_equity
    order_book_id date
    000001 2019-06-30 1.007034 6.082403e+09 6.246101e+09 4.747522e+09 4.714361e+09
    2019-12-31 1.010894 1.364662e+10 1.378563e+10 4.648447e+09 4.598352e+09
    ...
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is None:
        fields = FINANCIALS_FIELDS
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, FINANCIALS_FIELDS, "fields")
    result = get_client().execute(
        "fund.get_financials", order_book_ids, start_date, end_date, fields, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


FEE_FIELDS = [
    "purchase_fee",
    "subscription_fee",
    "redemption_fee",
    "management_fee",
    "custodian_fee",
    "sales_service_fee",
]


@export_as_api(namespace="fund")
def get_fee(order_book_ids, fee_type=None, charge_type="front", date=None, market_type="otc", market="cn"):
    """获取基金费率信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金order_book_id, str or list
    fee_type : str | list[str], optional
        费率类型，默认返回所有
    charge_type : str, optional
        前后端费率，取值为 'front' 或 'back'（默认 'front'）
    date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        日期
    market_type : str, optional
        场内/场外费率，可选 'exchange' 或 'otc'（默认 'otc'）
    market : str, optional
        默认是中国内地市场('cn')

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 基金合约代码
        - fee_type : str, 费率类型
        - fee_ratio : float, 费率比例
        - fee_value : float, 费率绝对值
        - inv_floor : float, 最小投资金额
        - inv_cap : float, 最大投资金额
        - share_floor : float, 最小份额
        - share_cap : float, 最大份额
        - holding_period_floor : int, 最短持有期（天）
        - holding_period_cap : int, 最长持有期（天）
        - return_floor : float, 收益下限
        - return_cap : float, 收益上限

    Examples
    --------
    >>> fund.get_fee('000001')

                         fee_ratio  fee_value  inv_floor    inv_cap  share_floor   share_cap  holding_period_floor  holding_period_cap  return_floor  return_cap
    order_book_id fee_type
    000001        purchase_fee        0.015        0.0        NaN          NaN          NaN                   NaN                 NaN           NaN           NaN
    000001        redemption_fee      0.005        0.0        NaN          1.0     1000000.0                  30.0               365.0         NaN

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date:
        date = ensure_date_int(date)
    if fee_type is None:
        fee_type = FEE_FIELDS
    else:
        fee_type = ensure_list_of_string(fee_type)
        check_items_in_container(fee_type, FEE_FIELDS, "fields")

    check_items_in_container(charge_type, ["front", "back"], "charge_type")
    market_type = market_type.lower()
    check_items_in_container(market_type, ['otc', 'exchange'], 'market_type')
    result = get_client().execute("fund.get_fee_v2", order_book_ids, fee_type, charge_type, date, market_type,
                                  market=market)
    if not result:
        return
    columns = [
        'order_book_id', 'fee_type', 'fee_ratio', 'fee_value',
        'inv_floor', 'inv_cap', 'share_floor', 'share_cap',
        'holding_period_floor', 'holding_period_cap',
        'return_floor', 'return_cap'
    ]
    df = pd.DataFrame(result, columns=columns)
    df.drop_duplicates(df.columns, inplace=True)
    df.set_index(["order_book_id", "fee_type"], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace="fund")
def get_transition_info(order_book_ids, market="cn"):
    """获取基金转型信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        合约代码
    market : str, optional
        默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - order_book_id : str, 基金合约号
        - transition_time : str, 转型次数。'0'-原始基金，'1'-第一次转型后基金，'2'-第二次转型后基金，以此类推
        - abbrev_symbol : str, 基金简称
        - symbol : str, 基金全称
        - amc : str, 基金公司名称
        - establishment_date : pandas.Timestamp, 成立日
        - listed_date : pandas.Timestamp, 上市日
        - de_listed_date : pandas.Timestamp, 退市日
        - stop_date : pandas.Timestamp, 终止日
        - accrued_daily : str, 货币基金收益分配方式(份额结转方式) 按日结转还是其他结转

    Examples
    --------
    >>> fund.get_transition_info('000014')

                              abbrev_symbol  accrued_daily         amc  ... listed_date   stop_date      symbol
    order_book_id transition_time                                           ...
    000014        0                       华夏一年债          False  华夏基金管理有限公司  ...  2013-03-19  2014-03-19  华夏一年定期开放债券
                  1                        华夏聚利          False  华夏基金管理有限公司  ...  2014-03-19  0000-00-00       华夏聚利债券
    """

    def _handler(group):
        if 1 < len(group):
            group.sort_values("transition_time", inplace=True)
            group.drop_duplicates(subset=["order_book_id"], inplace=True)
            return group
        return group

    order_book_ids = ensure_obs(order_book_ids, market)
    result = get_client().execute("fund.get_transition_info", order_book_ids, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df["order_book_id"] = df["order_book_id"].apply(lambda x: x[0:6])
    df = df.groupby(["order_book_id", "establishment_date"], as_index=False, group_keys=False).apply(_handler)
    # 未曾转型的基金不需要返回
    df = df.groupby(["order_book_id"], as_index=False, group_keys=False).apply(
        lambda g: g if 1 < len(g) else pd.DataFrame())
    df.dropna(inplace=True)
    if 0 == len(df):
        return
    df["transition_time"] = df["transition_time"].astype(int)
    df.set_index(["order_book_id", "transition_time"], inplace=True)
    return df.sort_index()


TRANSACTION_STATUS_FIELDS = [
    "subscribe_status",
    "redeem_status",
    "issue_status",
    "subscribe_upper_limit",
    "subscribe_lower_limit",
    "redeem_lower_limit",
    "redeem_upper_limit",
]


@export_as_api(namespace="fund")
def get_transaction_status(order_book_ids, start_date=None, end_date=None, fields=None, investor="institution",
                           market="cn"):
    """获取基金申购赎回相关信息

    Parameters
    ----------
    order_book_ids : str | list[str]
        基金代码
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        查询的结束日期，start_date ,end_date 不传参数时默认返回所有数据
    fields : str | list[str], optional
        查询字段，可选字段见下方返回，默认返回所有字段
    investor : str, optional
        默认为 institution；institution - 机构 , retail - 个人
    market : str, optional
        指定市场，目前仅有中国市场('cn')的基金数据

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - subscribe_status : str, 订阅状态。开放 - `Open`, 暂停 - `Suspended`, 限制大额申购 - `Limited`, 封闭期 - `Close`
        - redeem_status : str, 赎回状态。开放 - `Open`, 暂停 - `Suspended`, 限制大额赎回 - `Limited`, 封闭期 - `Close`
        - issue_status : str, 募集状态。募集中 - `Open`, 非募集期 - `Close`
        - subscribe_upper_limit : float, 申购上限（金额）
        - subscribe_lower_limit : float, 申购下限（金额）
        - redeem_lower_limit : float, 赎回下限（份额）
        - redeem_upper_limit : float, 赎回上限（份额），仅支持 ETF

    Examples
    --------
    获取个人申赎状态及相关信息

    >>> fund.get_transaction_status('040001',start_date='2020-11-01',end_date='2020-11-10',investor='retail')

                         subscribe_status redeem_status issue_status subscribe_upper_limit subscribe_lower_limit redeem_lower_limit
    order_book_id datetime
    040001        2020-11-01             Open          Open        Close                  None                     1                  1
                  2020-11-02             Open          Open        Close                  None                     1                  1
                  2020-11-03             Open          Open        Close                  None                     1                  1
                  2020-11-04             Open          Open        Close                  None                     1                  1
                  2020-11-05             Open          Open        Close                  None                     1                  1

    获取机构申赎状态及相关信息

    >>> fund.get_transaction_status('040001',start_date='2020-01-15',end_date='2020-01-25',investor='institution')

                         subscribe_status redeem_status issue_status subscribe_upper_limit subscribe_lower_limit redeem_lower_limit
    order_book_id datetime
    040001        2020-01-15             Open          Open        Close                  None                     1                  1
                  2020-01-16          Limited          Open        Close                 1e+06                     1                  1
                  2020-01-17          Limited          Open        Close                 1e+06                     1                  1
                  2020-01-18          Limited          Open        Close                 1e+06                     1                  1
                  2020-01-19          Limited          Open        Close                 1e+06                     1                  1
    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if start_date:
        start_date = to_date(start_date)
    if end_date:
        end_date = to_date(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, TRANSACTION_STATUS_FIELDS, 'fields')
    else:
        fields = TRANSACTION_STATUS_FIELDS

    check_items_in_container(investor, ['institution', 'retail'], 'investor')

    result = get_client().execute(
        "fund.get_transaction_status_v2", order_book_ids, fields, investor, market=market
    )
    if not result:
        return

    def _oid_process(x):
        x.set_index('datetime', inplace=True)
        x.sort_index(inplace=True)

        dates = pd.date_range(x.index.values[0], x.index.values[-1], freq='D')
        x = x.reindex(dates, method='ffill')
        x.index.names = ['datetime']

        x = x.where(x.notnull(), None)

        return x

    result = pd.DataFrame(result)

    result = result.groupby(['order_book_id']).apply(_oid_process)
    result.drop('order_book_id', axis=1, inplace=True)
    result.reset_index(inplace=True)

    result['datetime'] = result['datetime'].apply(to_date)

    if start_date:
        result = result[result['datetime'] >= start_date]
    if end_date:
        result = result[result['datetime'] <= end_date]

    result.set_index(['order_book_id', 'datetime'], inplace=True)

    result = result.reindex(columns=fields)
    return result


@export_as_api(namespace="fund")
def get_manager_weight_info(managers, start_date=None, end_date=None, asset_type="stock", manage_type="all", market="cn"):
    """获取基金经理人在管产品权重信息

    Parameters
    ----------
    managers : str | list[str]
        可传入基金经理 id 或名字。名字与 id 不能同时传入
    start_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        开始日期
    end_date : int | str | datetime.date | datetime.datetime | pandas.Timestamp, optional
        结束日期, start_date ,end_date 不传参数时默认返回所有数据
    asset_type : str, optional
        在管基金类型，默认为 stock。stock - 股票型，bond - 债券型
    manage_type : str, optional
        管理方式，默认为 all。independent - 独立管理，all - 所有参与管理
    market : str, optional
        指定市场，目前仅有中国市场('cn')的基金经理人衍生数据

    Returns
    -------
    pandas.DataFrame
        包含以下字段：
        - datetime : pandas.Timestamp, 在管时间
        - order_book_id : str, 在管基金代码
        - weight : float, 基金占经理人当期管理所有基金的规模比例
        - manager_name : str, 经理人名字

    Examples
    --------
    获取 id 为 101002315 的基金经理在管产品权重信息

    >>> fund.get_manager_weight_info('101002315',asset_type='bond',manage_type='independent',start_date=20200101)

    manager_id datetime    order_book_id    weight manager_name
    101002315  2020-03-31        007834      0.297317  蔡宾
    101002315  2020-03-31        007833      0.297317  蔡宾
    ...

    获取某基金经理在管产品权重信息

    >>> fund.get_manager_weight_info('李博',asset_type='stock',manage_type='independent',start_date=20200101)

    manager_id datetime    order_book_id    weight manager_name
    101001503  2020-03-31        001144      0.389673  李博
    101001503  2020-03-31        090004      0.610327  李博
    ...

    """
    managers = ensure_list_of_string(managers)
    # 检查manager中是否同时有人员编码或姓名
    if len(set(x.isdigit() for x in managers)) > 1:
        raise ValueError("couldn't get manager_id and name at the same time")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    result = get_client().execute("fund.get_manager_weight_info", managers, start_date, end_date, asset_type, manage_type, market)

    if not result:
        return

    df = pd.DataFrame(result)
    df.set_index(keys=["manager_id", "datetime"], inplace=True)
    return df.sort_index()
