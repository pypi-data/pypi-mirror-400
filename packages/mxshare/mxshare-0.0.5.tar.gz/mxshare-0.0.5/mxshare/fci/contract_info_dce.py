#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/12/31 16:00
Desc: 大连商品交易所-业务数据-交易参数-合约信息
http://www.dce.com.cn/dce/channel/list/180.html
"""

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import time
import random
from fake_useragent import UserAgent


# -------------------------- UA随机化 + 操作间隔随机化配置 --------------------------
def get_random_ua():
    """随机生成符合真实浏览器特征的User-Agent"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        # 兜底UA列表，避免依赖库失效
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/116.0 Safari/537.36",
        ]
        return random.choice(ua_list)


def random_sleep(min_seconds=1, max_seconds=4):
    """模拟人工操作的随机间隔（避免固定等待时长）"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def contract_info_dce(instrument: str = "Future") -> pd.DataFrame:
    """
    大连商品交易所-业务数据-交易参数-合约信息
    http://www.dce.com.cn/dce/channel/list/180.html
    :param instrument: 合约类型
    :type date: str
    :return: 交易参数汇总查询
    :rtype: pandas.DataFrame
    """
    # 映射合约类型到trade_type编码
    instrument_mapping = {"Future": "1", "Option": "2"}
    # 校验参数合法性
    if instrument not in instrument_mapping:
        raise ValueError(f"instrument参数仅支持：{list(instrument_mapping.keys())}")
    source_url = "http://www.dce.com.cn/dce/channel/list/180.html"
    target_api = "http://www.dce.com.cn/dcereport/publicweb/tradepara/contractInfo"

    request_data = {
        "varietyId": "all",
        "tradeType": instrument_mapping[instrument],
        "lang": "zh",
    }

    custom_headers = {
        "accept": "application/json, text/plain, */*",
        "cache-control": "no-cache",
        "clientid": "web",
        "pragma": "no-cache",
        "referer": source_url,
        "origin": "https://www.dce.com.cn",
        "content-type": "application/json",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            # headless=True, # Linux
            slow_mo=random.randint(100, 300),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--no-sandbox",
                "--disable-extensions-except=",
                "--disable-default-apps",
                "--start-maximized",
                # "--start-fullscreen",  # Linux
                # "--disable-dev-shm-usage",  # Linux下解决/dev/shm内存不足问题
                # "--single-process",  # 可选：Linux轻量环境单进程模式
            ],
        )

        context = browser.new_context(
            user_agent=get_random_ua(),
            viewport=None,
            ignore_https_errors=True,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            geolocation={"latitude": 39.9042, "longitude": 116.4074},
            # locale="zh-CN.UTF-8",  # Linux下指定UTF-8字符集，避免中文乱码
        )
        page = context.new_page()

        try:
            # 正在加载来源页面，生成有效会话...
            page.goto(
                source_url,
                wait_until="domcontentloaded",
                timeout=random.randint(20000, 35000),
            )

            # 等待页面关键元素加载
            page.wait_for_selector(
                "body", state="visible", timeout=random.randint(15000, 25000)
            )
            random_sleep(2, 5)

            # 模拟真人滚动页面（上下滚动）
            page.mouse.wheel(delta_y=random.randint(200, 500), delta_x=0)
            random_sleep(1, 3)
            page.mouse.wheel(delta_y=random.randint(-300, -100), delta_x=0)
            random_sleep(1, 2)

            try:
                page.hover("nav", timeout=5000)  # 悬停导航栏，触发页面事件
            except:
                pass

            page_content = page.content()
            if len(page_content.strip()) < 100:
                raise Exception("页面加载失败，内容为空")

            # -------------------------- 请求重试机制（模拟人工重试） --------------------------
            max_retry = 1
            retry_count = 0
            response = None
            while retry_count < max_retry:
                try:
                    # 正在发送接口请求...
                    response = context.request.post(
                        url=target_api,
                        data=json.dumps(request_data),
                        headers=custom_headers,
                        timeout=random.randint(25000, 35000),  # 随机超时
                    )
                    if response.ok:
                        break
                except Exception as e:
                    retry_count += 1
                    random_sleep(3, 5)
                    if retry_count >= max_retry:
                        raise e

            if response.ok:
                result = response.json()
                df = pd.DataFrame(result["data"])
                return df
            else:
                return response
        except Exception as e:
            raise e
        finally:
            random_sleep(1, 3)
            browser.close()


if __name__ == "__main__":
    contract_info_dce_df = contract_info_dce()
    print(contract_info_dce_df)
