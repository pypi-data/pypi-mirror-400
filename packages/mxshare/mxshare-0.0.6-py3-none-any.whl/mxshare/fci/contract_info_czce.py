#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 郑州商品交易所-交易数据-参考数据
https://www.czce.com.cn/cn/jysj/cksj/H077003022index_1.htm
"""

import xml.etree.ElementTree as ET

import pandas as pd
import requests


def contract_info_czce(
    date: str = "20251219", instrument: str = "Future"
) -> pd.DataFrame:
    """
    郑州商品交易所-交易数据-参考数据
    https://www.czce.com.cn/cn/jysj/cksj/H077003022index_1.htm
    :param date: 查询日期
    :param instrument: 合约类型
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    # 校验参数合法性
    if instrument not in ["Future", "Option"]:
        raise ValueError("instrument参数只能为'Future'或'Option'")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/84.0.4147.89 Safari/537.36",
        "Host": "www.czce.com.cn",
    }
    url = f"http://www.czce.com.cn/cn/DFSStaticFiles/{instrument}/{date[:4]}/{date}/{instrument}DataReferenceData.xml"
    r = requests.get(url, headers=headers)
    xml_data = r.text
    # 解析 XML
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    # 获取所有的记录
    records = root.findall(".//Contract")
    # 解析数据并填充到列表中
    data = []
    for record in records:
        # 对于每个记录，创建一个字典
        row_data = {}
        for field in record:
            row_data[field.tag] = field.text
        # 将字典添加到数据列表中
        data.append(row_data)
    df = pd.DataFrame(data)

    return df


if __name__ == "__main__":
    contract_info_czce = contract_info_czce(date="20251219")
    print(contract_info_czce)