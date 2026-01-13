#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
babaclose = pd.read_csv('../financeda/data/stock_BABA.csv')['Close']
from financeda.class_price_list import PriceList

pl = PriceList(babaclose)
# flag = pl.bind(babaclose)

# print(flag,pl.Stock_Returns)

aa = pl.Sum_Return_Ratio
print(aa)
print(pl.Stock_Ratio)

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
babaclose = pd.read_csv('../financeda/data/stock_BABA.csv')['Close']

from financeda.class_price_list import PriceList
pl = PriceList()
print(pl)
flag = pl.sample()
print(pl.Daily_Return_Ratio_Log)
print(flag,pl.Stock_Ratio)

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.class_stock_data import StockData

sd_ = StockData(source="tushare")
df = sd_.load_stock_csv('BABA',start_date='2025-01-01',end_date='2025-12-31',csv_file=None)
print(df.tail())

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.class_stock_data import StockData

sd_ = StockData(source="tushare",token="aac3815814723db39100bf3cecbb0b2b73144da433d708d77d1f4c5e")
# sd_.set_token("aac3815814723db39100bf3cecbb0b2b73144da433d708d77d1f4c5e")
df = sd_.load_stock_csv('000651.sz')
print(df.tail())
#%%
print(sd_.token)

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.class_stock_data import StockData
sd_ = StockData(sample="gl")
print(sd_.DF.tail())

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.class_stock_data import StockData
from financeda.functions_single import plot_candle,stock_diff,stock_tsa,stock_tests
df_ = StockData(sample="gl").DF
print(df_.tail())

stock_tsa(df_)

plot_candle(df_)
stock_diff(df_)
stock_tests(df_)

#%%

stocks = {'600031.SH': '三一重工', '601138.SH': '工业富联', '000768.SZ': '中航西飞', '600519.SH': '贵州茅台'}

#%%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.class_stock_data import StockData
from financeda.class_stock_po import StockPO

sdpo = StockPO(stocks, source="tushare",token="aac3815814723db39100bf3cecbb0b2b73144da433d708d77d1f4c5e")
#%%
print(sdpo.data.tail())
w,rr = sdpo.po_random()
print(w, rr)
sdpo.po_mc(2000)
opts = sdpo.po_max_sharpe()
optv = sdpo.po_min_vol()
print(opts,optv)
sdpo.po_ef()
sdpo.po_cml()

#%%
# stocks = {'600031.SH': '三一重工', '601138.SH': '工业富联', '000768.SZ': '中航西飞', '600519.SH': '贵州茅台','005944.SZ':'比亚迪'}

# %%
import  yfinance as yf
a = yf.download('BABA',period='max',auto_adjust=True)
print(a.tail(3))

# %%
import sys
sys.path.append("e:/OK_FinDA/")
import pandas as pd
from financeda.functions_ffreg  import ff_reg
stocks={
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
df = ff_reg(stocks=stocks, start_date='2024-10-01', end_date='2025-10-31', mode=5)
print(df)
outfile = "ff_reg.csv"
df.to_csv(outfile)
# %%
