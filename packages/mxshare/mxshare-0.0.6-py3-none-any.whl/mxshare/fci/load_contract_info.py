import os
import pandas as pd
import logging
import argparse 
from concurrent.futures import ThreadPoolExecutor, as_completed
import contract_info_dce as dce
# import mxshare.fci.contract_info_szse as szse
# import mxshare.fci.contract_info_czce as czce
# import mxshare.fci.contract_info_cffex as cffex
# import mxshare.fci.contract_info_gfex as gfex
# import mxshare.fci.contract_info_ine as ine
# import mxshare.fci.contract_info_shfe as shfe

# ===================== 日志配置 =====================
def setup_logger():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# ===================== 解析命令行参数 =====================
def parse_args():
    parser = argparse.ArgumentParser(description='获取并导出交易所合约信息')
    # 日期参数：必传，格式如20251219
    parser.add_argument('--date', default='20260107', help='查询日期，格式为YYYYMMDD（如20251219）')
    # 输出目录：可选，默认/data/airflow_exec2/commodityexch
    parser.add_argument('--output', default='/data/airflow_exec2/commodityexch', help=f'输出根目录（默认：/data/airflow_exec2/commodityexch）')
    # 线程数：可选，默认1，需为正整数
    parser.add_argument('--workers', type=int, default=1, help=f'最大线程数（默认：1，需为正整数）')
    
    args = parser.parse_args()
    
    # 验证线程数必须为正整数
    if args.workers <= 0:
        parser.error(f'--workers 必须为正整数，实际值：{args.workers}')
    
    return args

# ===================== 核心配置 =====================
args = parse_args()
QUERY_DATE = args.date
OUTPUT_ROOT = args.output
MAX_WORKERS = args.workers

# 从日期解析年和年月
YEAR = QUERY_DATE[:4]
YEAR_MONTH_DAY = QUERY_DATE

BASE_DATA_TYPES = ["Option", "Future"]

EXCHANGE_CONFIG = {
    "dce": {
        "module": dce,
        "func_name": "contract_info_dce",
        "data_type_mode": "original",
        "param_rules": {"need_date": False, "need_instrument": True},
        "field_mapping": {
            "Option": {
                "variety": "品种",
                "contractId": "合约代码",
                "unit": "交易单位",
                "tick": "最小变动价位",
                "startTradeDate": "开始交易日",
                "endTradeDate": "最后交易日",
                "endDeliveryDate": "最后交割日",
            },
            "Future": {
                "variety": "品种",
                "contractId": "合约代码",
                "unit": "交易单位",
                "tick": "最小变动价位",
                "startTradeDate": "开始交易日",
                "endTradeDate": "最后交易日",
                "endDeliveryDate": "最后交割日",
            }
        }
    },
    # "szse": {
    #     "module": szse,
    #     "func_name": "contract_info_szse",
    #     "data_type_mode": "original",
    #     "param_rules": {"need_date": False, "need_instrument": False},
    #     "field_mapping": {
    #         "all": {
    #             "hybm": "合约编码",
    #             "hzjyrq": "最后交易日",
    #             "xqrq": "行权日",
    #             "dqrq": "到期日",
    #             "jsrq": "交收日",
    #         }
    #     }
    # },
    # "czce": {
    #     "module": czce,
    #     "func_name": "contract_info_czce",
    #     "data_type_mode": "original",
    #     "param_rules": {"need_date": True, "need_instrument": True},
    #     "field_mapping": {
    #         "Option": {
    #             "Name": "品种",
    #             "CtrCd": "合约代码",
    #             "MsrmntUnt": "交易单位",
    #             "TckSz": "最小变动价位",
    #             "FrstTrdDt": "开始交易日",
    #             "LstTrdDt": "最后交易日",
    #             "SettleDt": "结算日",
    #             "ExpiryDt": "到期日",
    #         },
    #         "Future": {
    #             "Name": "品种",
    #             "CtrCd": "合约代码",
    #             "MsrmntUnt": "交易单位",
    #             "TckSz": "最小变动价位",
    #             "FrstTrdDt": "开始交易日",
    #             "LstTrdDt": "最后交易日",
    #             "DlvryNtcDt": "交割通知日",
    #             "DlvrySettleDt": "交割结算日",
    #             "LstDlvryDt": "最后交割日",
    #             "LstDlvryDtBoard": "车（船）板最后交割日",
    #         }
    #     }
    # },
    # "cffex": {
    #     "module": cffex,
    #     "func_name": "contract_info_cffex",
    #     "data_type_mode": "original",
    #     "param_rules": {"need_date": True, "need_instrument": False},
    #     "field_mapping": {
    #         "all": {
    #             "INSTRUMENT_ID": "合约代码",
    #             "OPEN_DATE": "上市日",
    #             "END_TRADING_DAY": "最后交易日",
    #         }
    #     }
    # },
    # "gfex": {
    #     "module": gfex,
    #     "func_name": "contract_info_gfex",
    #     "data_type_mode": "original",
    #     "param_rules": {"need_date": False, "need_instrument": True},
    #     "field_mapping": {
    #         "Option": {
    #             "contractId": "合约代码",
    #             "variety": "品种",
    #             "unit": "交易单位",
    #             "tick": "最小变动价位",
    #             "startTradeDate": "开始交易日",
    #             "endTradeDate": "最后交易日",
    #             "endDeliveryDate0": "最后交割日",
    #         },
    #         "Future": {
    #             "contractId": "合约代码",
    #             "variety": "品种",
    #             "unit": "交易单位",
    #             "tick": "最小变动价位",
    #             "startTradeDate": "开始交易日",
    #             "endTradeDate": "最后交易日",
    #             "endDeliveryDate0": "最后交割日",
    #         }
    #     }
    # },
    # "ine": {
    #     "module": ine,
    #     "func_name": "contract_info_ine",
    #     "data_type_mode": "lower",
    #     "param_rules": {"need_date": True, "need_instrument": True},
    #     "field_mapping": {
    #         "Option": {
    #             "COMMODITYNAME": "品种",
    #             "INSTRUMENTID": "合约代码",
    #             "TRADEUNIT": "交易单位",
    #             "PRICETICK": "最小变动价位",
    #             "OPENDATE": "开始交易日",
    #             "EXPIREDATE": "最后交易日",
    #         },
    #         "Future": {
    #             "INSTRUMENTID": "合约代码",
    #             "OPENDATE": "上市日",
    #             "EXPIREDATE": "到期日",
    #             "STARTDELIVDATE": "开始交割日",
    #             "ENDDELIVDATE": "最后交割日",
    #         }
    #     }
    # },
    # "shfe": {
    #     "module": shfe,
    #     "func_name": "contract_info_shfe",
    #     "data_type_mode": "lower",
    #     "param_rules": {"need_date": True, "need_instrument": True},
    #     "field_mapping": {
    #         "Option": {
    #             "COMMODITYNAME": "品种",
    #             "INSTRUMENTID": "合约代码",
    #             "TRADEUNIT": "交易单位",
    #             "PRICETICK": "最小变动价位",
    #             "OPENDATE": "开始交易日",
    #             "EXPIREDATE": "最后交易日",
    #         },
    #         "Future": {
    #             "INSTRUMENTID": "合约代码",
    #             "OPENDATE": "上市日",
    #             "EXPIREDATE": "到期日",
    #             "STARTDELIVDATE": "开始交割日",
    #             "ENDDELIVDATE": "最后交割日"
    #         }
    #     }
    # }
}

# ===================== 工具函数 =====================
def create_output_dir(exchange):
    """创建交易所对应的层级目录"""
    dir_path = os.path.join(OUTPUT_ROOT, exchange, YEAR, YEAR_MONTH_DAY)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"创建输出目录: {dir_path}")
    return dir_path

def adapt_data_type(data_type: str, mode: str) -> str:
    if mode == "lower":
        return data_type.lower()
    elif mode == "original":
        return data_type
    else:
        return data_type

def is_data_empty(data) -> bool:
    """
    通用空值判断（兼容列表/字典/DataFrame）
    :param data: 待判断数据
    :return: 是否为空
    """
    if data is None:
        return True
    # DataFrame空值判断
    elif isinstance(data, pd.DataFrame):
        return data.empty
    # 列表/元组空值判断
    elif isinstance(data, (list, tuple)):
        return len(data) == 0
    # 字典空值判断
    elif isinstance(data, dict):
        return len(data) == 0
    # 其他类型默认非空
    else:
        return False

def rename_fields(data, field_mapping: dict, data_type: str) -> pd.DataFrame or list:
    """
    兼容DataFrame/列表的字段过滤+重命名
    :param data: 原始数据（DataFrame/列表）
    :param field_mapping: 字段映射
    :param data_type: 数据类型（Option/Future/all）
    :return: 处理后的数据（保持原数据类型）
    """
    # 空值直接返回
    if is_data_empty(data):
        logger.warning(f"{data_type} 数据为空，跳过字段重命名")
        return data
    
    # 获取对应类型的映射规则
    type_mapping = field_mapping.get(data_type, field_mapping.get("all", {}))
    if not isinstance(type_mapping, dict) or len(type_mapping) == 0:
        logger.warning(f"{data_type} 无有效字段映射，返回原始数据")
        return data
    
    # 处理DataFrame类型（GFEX返回的类型）
    if isinstance(data, pd.DataFrame):
        # 1. 过滤列：仅保留映射中的原始字段
        valid_columns = [col for col in type_mapping.keys() if col in data.columns]
        filtered_df = data[valid_columns].copy()
        # 2. 重命名列
        filtered_df.rename(columns=type_mapping, inplace=True)
        return filtered_df
    
    # 处理列表（字典）类型
    elif isinstance(data, list):
        renamed_data = []
        for row in data:
            if not isinstance(row, dict):
                renamed_data.append(row)
                continue
            new_row = {}
            # 仅保留映射中的字段
            for old_field, new_field in type_mapping.items():
                if old_field in row:
                    new_row[new_field] = row[old_field]
            renamed_data.append(new_row)
        return renamed_data
    
    # 其他类型直接返回
    else:
        logger.warning(f"不支持的数据类型: {type(data)}，返回原始数据")
        return data

# ===================== 核心逻辑 =====================
def get_contract_data(exchange: str, data_type: str) -> tuple:
    """兼容DataFrame的合约数据获取逻辑"""
    try:
        config = EXCHANGE_CONFIG[exchange]
        param_rules = config["param_rules"]
        
        logger.info(f"处理 {exchange.upper()} - {data_type} | "
                    f"参数规则：date={param_rules['need_date']}, instrument={param_rules['need_instrument']}")
        
        # 组装调用参数
        call_kwargs = {}
        if param_rules["need_date"]:
            call_kwargs["date"] = QUERY_DATE
        if param_rules["need_instrument"]:
            adapted_data_type = adapt_data_type(data_type, config["data_type_mode"])
            call_kwargs["instrument"] = adapted_data_type
        
        # 执行查询
        query_func = getattr(config["module"], config["func_name"])
        raw_data = query_func(**call_kwargs)
        
        # 字段过滤+重命名（兼容DataFrame/列表）
        processed_data = rename_fields(raw_data, config["field_mapping"], data_type)
        
        # 日志输出数据量（兼容不同类型）
        if isinstance(processed_data, pd.DataFrame):
            data_count = len(processed_data)
        elif isinstance(processed_data, (list, tuple)):
            data_count = len(processed_data)
        else:
            data_count = "未知"
        logger.info(f"{exchange.upper()} - {data_type} | 处理后数据量: {data_count}")
        
        return (exchange, data_type, processed_data, None)
    except Exception as e:
        error_msg = f"{exchange.upper()} - {data_type} 处理失败: {str(e)}"
        logger.error(error_msg)
        return (exchange, data_type, None, error_msg)

def export_to_csv(exchange: str, data_type: str, data) -> None:
    """通用CSV导出（兼容DataFrame/列表）"""
    if is_data_empty(data):
        logger.warning(f"{exchange.upper()} - {data_type} 无有效数据，跳过导出")
        return

    # 创建交易所对应的层级目录
    output_dir = create_output_dir(exchange)

    # 构建文件名
    if exchange in ("cffex", "szse"):
        filename = f"{exchange}_all_cidInfo_{QUERY_DATE}.csv"
    else:
        filename = f"{exchange}_{data_type.lower()}_cidInfo_{QUERY_DATE}.csv"
    filepath = os.path.join(output_dir, filename)

    try:
        # 统一转换为DataFrame（兼容列表/字典） 
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            data_df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            data_df = data
        else:
            logger.warning(f"{exchange.upper()} - {data_type} 数据格式不支持（{type(data)}），跳过导出")
            return
        
        # 导出CSV
        data_df.to_csv(filepath, index=False, encoding='utf_8_sig')
        logger.info(f"✅ 导出成功: {filepath} | 字段列表: {list(data_df.columns)}")
    except Exception as e:
        logger.error(f"❌ 导出失败 {filepath}: {str(e)}")

def main():
    # 无需提前创建根目录，在create_output_dir中会按交易所创建完整路径

    # 构建任务列表
    tasks = []
    for exchange in EXCHANGE_CONFIG.keys():
        if exchange in ("cffex", "szse"):
            tasks.append((exchange, "all"))
        else:
            for data_type in BASE_DATA_TYPES:
                tasks.append((exchange, data_type))

    # 并行执行
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {
            executor.submit(get_contract_data, exchange, data_type): (exchange, data_type)
            for exchange, data_type in tasks
        }

        # 处理结果
        for future in as_completed(future_to_task):
            exchange, data_type = future_to_task[future]
            try:
                _, _, data, error = future.result()
                if error:
                    continue
                export_to_csv(exchange, data_type, data)
            except Exception as e:
                logger.error(f"处理 {exchange.upper()} - {data_type} 结果出错: {str(e)}")

    logger.info("\n🎉 所有任务执行完成！")

if __name__ == "__main__":
    main()