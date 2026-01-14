#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 广州期货交易所-业务/服务-合约信息
http://www.gfex.com.cn/gfex/hyxx/ywcs.shtml
"""

import pandas as pd
import requests


def contract_info_gfex(instrument: str = "Future") -> pd.DataFrame:
    """
    广州期货交易所-业务/服务-合约信息
    http://www.gfex.com.cn/gfex/hyxx/ywcs.shtml
    :param instrument: 合约类型
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    # 映射合约类型到trade_type编码
    instrument_mapping = {"Future": "0", "Option": "1"}
    # 校验参数合法性
    if instrument not in instrument_mapping:
        raise ValueError(f"instrument参数仅支持：{list(instrument_mapping.keys())}")

    url = "http://www.gfex.com.cn/u/interfacesWebTtQueryContractInfo/loadList"
    params = {
        "variety": "",
        "trade_type": instrument_mapping[instrument],
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        r = requests.post(url, params=params, headers=headers)
        data_json = r.json()
        df = pd.DataFrame(data_json["data"])
        # 空数据处理
        if df.empty:
            print(f"提示：{instrument}类型暂无合约数据")
        return df

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"请求失败：{str(e)}")
    except ValueError as e:
        raise ValueError(f"解析数据失败：{str(e)}")


if __name__ == "__main__":
    contract_info_gfex_df = contract_info_gfex()
    print(contract_info_gfex_df)
