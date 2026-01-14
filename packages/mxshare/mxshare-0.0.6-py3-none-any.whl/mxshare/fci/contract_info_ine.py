#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 上海国际能源交易中心-业务指南-交易参数汇总(期货)
https://www.ine.cn/reports/businessdata/prmsummary/
"""

import pandas as pd
import requests


def contract_info_ine(
    date: str = "20251219", instrument: str = "option"
) -> pd.DataFrame:
    """
    上海国际能源交易中心-业务指南-交易参数汇总(期货)
    https://www.ine.cn/reports/businessdata/prmsummary/
    :param date: 查询日期; 交易日
    :param instrument: 合约类型
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    # 校验参数合法性
    if instrument not in ["future", "option"]:
        raise ValueError("instrument参数只能为'future'或'option'")

    # 定义不同类型的配置
    config = {
        "future": {
            "data_key": "ContractBaseInfo",
        },
        "option": {
            "data_key": "OptionContractBaseInfo",
        },
    }[instrument]
    url = (
        f"https://www.ine.cn/data/busiparamdata/{instrument}/ContractBaseInfo{date}.dat"
    )
    params = {"rnd": "0.8312696798757147"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, params=params, headers=headers)
        data_json = r.json()
        df = pd.DataFrame(data_json[config["data_key"]])
        return df
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"请求失败：{str(e)}")
    except ValueError as e:
        raise ValueError(f"解析数据失败：{str(e)}")


if __name__ == "__main__":
    contract_info_ine_df = contract_info_ine(date="20251219")
    print(contract_info_ine_df)
