#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 上海期货交易所-交易所服务-业务数据-交易参数汇总查询
https://www.shfe.com.cn/reports/businessdata/prmsummary/
"""

import pandas as pd
import requests


def contract_info_shfe(
    date: str = "20251219", instrument: str = "future"
) -> pd.DataFrame:
    """
    上海期货交易所-交易所服务-业务数据-交易参数汇总查询
    https://www.shfe.com.cn/reports/businessdata/prmsummary/
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

    # 请求数据
    url = f"https://www.shfe.com.cn/data/busiparamdata/{instrument}/ContractBaseInfo{date}.dat"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()  # 抛出HTTP请求异常
        data_json = r.json()

        # 构建DataFrame
        df = pd.DataFrame(data_json[config["data_key"]])
        return df
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"请求失败：{str(e)}")
    except ValueError as e:
        raise ValueError(f"解析数据失败：{str(e)}")


if __name__ == "__main__":
    contract_info_shfe_df = contract_info_shfe(date="20251219")
    print(contract_info_shfe_df)
