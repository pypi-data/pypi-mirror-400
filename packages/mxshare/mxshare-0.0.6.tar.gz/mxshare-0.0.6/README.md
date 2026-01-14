# mxshare
A demo Python package for personal sharing, used to obtain contract parameter data of commodity exchanges.

## 功能介绍
当前仅包含 `fci` 核心模块（Futures & Contract Info），专注于商品交易所合约参数数据获取，支持：
- 期货（Future）合约参数查询
- 期权（Option）合约参数查询
- 已适配6大交易所合约数据获取，分别为：
  1.  上海期货交易所（SHFE）
  2.  深圳证券交易所（SZSE）
  3.  郑州商品交易所（CZCE）
  4.  中国金融期货交易所（CFFEX）
  5.  广州期货交易所（GFEX）
  6.  上海国际能源交易中心（INE）

## 安装
```bash
pip install mxshare
```

## 使用示例
```python
import mxshare.fci.contract_info_shfe as shfe

shfe.contract_info_shfe(date='20251226', instrument='option')
```

输出示例：
```
     INSTRUMENTID  OPENDATE PRICETICK EXCHANGEID SETTLEMENTGROUPID TRADINGDAY COMMODITYNAME EXPIREDATE COMMODITYID TRADEUNIT
0      sc2602C375  20251218      0.05       SHFE          00000001   20251226            原油   20260114          sc      1000
1      sc2602C380  20251127      0.05       SHFE          00000001   20251226            原油   20260114          sc      1000
2      sc2602C385  20251125      0.05       SHFE          00000001   20251226            原油   20260114          sc      1000
3      sc2602C390  20251121      0.05       SHFE          00000001   20251226            原油   20260114          sc      1000
4      sc2602C395  20251110      0.05       SHFE          00000001   20251226            原油   20260114          sc      1000
...           ...       ...       ...        ...               ...        ...           ...        ...         ...       ...
5363  op2603P4500  20251205         1       SHFE          00000001   20251226         胶版印刷纸   20260213          op        40

[5364 rows x 10 columns]
```

## Acknowledgement

Thanks for the data provided by [深证证券交易所网站](http://www.szse.cn/);

Thanks for the data provided by [中国金融期货交易所网站](http://www.cffex.com.cn/);

Thanks for the data provided by [上海期货交易所网站](http://www.shfe.com.cn/);

Thanks for the data provided by [郑州商品交易所网站](http://www.czce.com.cn/);

Thanks for the data provided by [上海国际能源交易中心网站](http://www.ine.com.cn/);

Thanks for the data provided by [广州期货交易所交易中心网站](http://www.gfex.com.cn/);