#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 深圳证券交易所-行情数据-当日合约
https://www.szse.cn/option/quotation/contract/daycontract/index.html
"""

import requests
import pandas as pd
import time
import random

def contract_info_szse() -> pd.DataFrame:
    """
    封装分页逻辑，单次调用获取全部合约数据（内部自动分页）
    """
    url = "https://www.szse.cn/api/report/ShowReport/data"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.szse.cn/option/quotation/contract/daycontract/index.html"
    }
    all_data = []
    page = 1

    while True:
        params = {
            "SHOWTYPE": "JSON",
            "CATALOGID": "option_drhy",
            "TABKEY": "tab1",
            "PAGENO": page,
            "random": str(time.time())
        }
        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)
            res.raise_for_status()
            page_data = res.json()[0].get("data", [])
            if not page_data:
                break
            all_data.extend(page_data)
            page += 1
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            print(f"分页请求异常：{e}")
            break

    return pd.DataFrame(all_data)


if __name__ == "__main__":
    contract_info_szse_df = contract_info_szse()
    print(contract_info_szse_df)
