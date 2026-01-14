#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/19 16:30
Desc: 中国金融期货交易所-数据-交易参数
http://www.cffex.com.cn/jycs/
"""

import xml.etree.ElementTree as ET

import pandas as pd
import requests


def contract_info_cffex(date: str = "20251219") -> pd.DataFrame:
    """
    中国金融期货交易所-数据-交易参数
    http://www.cffex.com.cn/jycs/
    :param date: 查询日期
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
    url = f"http://www.cffex.com.cn/sj/jycs/{date[:6]}/{date[6:]}/index.xml"
    r = requests.get(url, headers=headers)
    xml_data = r.text
    # 解析 XML
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()
    # 获取所有的记录
    records = root.findall(".//INDEX")
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
    contract_info_cffex_df = contract_info_cffex(date="20251219")
    print(contract_info_cffex_df)
