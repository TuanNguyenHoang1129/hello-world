import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import cufflinks as cf
import plotly.graph_objects as go
import numpy as np
import vectorbt as vbt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import trendln
from collections import namedtuple
import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as pyo
import talib
import pandas_ta

import warnings
warnings.filterwarnings('ignore')



# ----------------------------------------------------------------------------------------------------
# FUNTION TO FIND ALL STOCK FILES:
def find_files(stock_fol):
	all_files = []
	for dirs,roots,files in os.walk('%s'%(stock_fol)):
		for file in files:
			all_files.append((dirs+'\\'+file))
	return all_files



# ----------------------------------------------------------------------------------------------------
# FUNTION TO FIND ALL STOCK FILES:

def test_signal(data_source,entries,exits,buy_price='close',buy_lag=0,direction='longonly', accumulate='addonly',
									   sl_stop=0.1, sl_trail=True, tp_stop = 0.1, 
									   fees=0.0015, freq= '1D'):
	data = data_source.copy()
	#	 Checking profit:
	bt_pf = vbt.Portfolio.from_signals(close=data[buy_price].shift(buy_lag), entries = entries,
									exits=exits,
									direction=direction, 
									accumulate=accumulate,
									sl_stop=sl_stop, sl_trail=sl_trail, tp_stop = tp_stop, 
									fees=fees, freq= freq)


	#res = res.append(pd.DataFrame({stock_name:bt_pf.stats()}).T,ignore_index=False)
	# res = pd.concat([res, pd.DataFrame({stock_name:bt_pf.stats()}).T],ignore_index=False)
	return bt_pf