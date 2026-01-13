#%%
from financeDA import hello_financeda
hello_financeda()

#%%
from financeDA import ff_reg
code_name={
        "600100.SH": "同方股份",
        "600626.SH": "申达股份",
        "000630.SZ": "铜陵有色",
        "000850.SZ": "华茂股份",
        "600368.SH": "五洲交通",
        "603766.SH": "隆鑫通用",
        "600105.SH": "永鼎股份",
        "600603.SH": "广汇物流",
        "002344.SZ": "海宁皮城",
        "000407.SZ": "胜利股份",
        "000883.SZ": "湖北能源"
        }
df = ff_reg(stocks=code_name, start_date='2024-10-01', end_date='2025-10-31', mode=5)
print(df)
# outfile = "/FFReg_2025.csv"
# df.to_csv(outfile,index=False)

#%%
from financeDA.class_stock_data import StockData # 股票数据，[Close, High, Low, Open, Volume] 及主要扩展指标[Diff, Signal, Close_Open, Returns, Log_Returns, 42d, 252d, Mov_Vol等]
from financeDA import stock_diff, stock_tsa, stock_tests # 可视化：折线图、蜡烛图、直方图、QQ图、股票收益率、股票时间序列分析、股票统计测试

df_stock = StockData("BABA", start="2020-01-01", end="2025-12-20", source="yfinance").DF
print(df_stock.head())

stock_diff(df_stock)
stock_tsa(df_stock)
stock_tests(df_stock)

# %%
import numpy as np
import pandas as pd
from financeDA.class_stock_data import StockData
from financeDA.class_stock_po import StockPO

stocks = {
        '600031.SH': '三一重工', 
        '601138.SH': '工业富联', 
        '000768.SZ': '中航西飞', 
        '600519.SH': '贵州茅台'
        }

sdpo = StockPO()

print(sdpo.data.tail())
weights,results = sdpo.po_random()
print(weights,results)

sdpo.po_mc(200000)  #默认2000次，可加大模拟次数

opts = sdpo.po_max_sharpe()
optv = sdpo.po_min_vol()
print(opts, optv) #手动计算最大夏普率和最小波动率的投资组合权重

sdpo.po_ef(trets=np.linspace(0.06, 0.15, 30))  # 手动计算有效边界，可不断调整trets的取值以获取最佳效果
sdpo.po_cml() # 手动计算有效边界下的最大夏普率组合(资本市场线)
#%%
