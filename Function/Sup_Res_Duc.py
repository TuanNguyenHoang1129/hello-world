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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO CREATE SUPPORT AND RESISTANCE:
def sup_res_obs(data_source,interval=10,close_='close',open_='open',high_='high',low_='low'):
	data = data_source.copy()
	data['swing_high'] = (data[close_][(data[high_]>talib.MAX(data[high_], interval).shift(1)) & 
									(data[close_].shift(1) < data[close_].shift(0))  &  
									(data[close_].shift(-1) < data[close_].shift(0))
									])#.shift(1)
	data['swing_high'] = data['swing_high'].shift(1)

	data['upper_high'] = (data['high'].shift(1))[data['swing_high']==data['swing_high']]
	data['lower_high'] = (data['low'].shift(1))[data['swing_high']==data['swing_high']]
	data['tf_upper_high'] = data['upper_high'].fillna(method='ffill')
	data['tf_lower_hgih'] = data['lower_high'].fillna(method='ffill')

	data['check_cross_high'] = data[close_][(data[close_] > data['tf_upper_high']) &
										(data[close_].shift(1) < data[close_].shift(0))  &  
											(data[close_].shift(-1) < data[close_].shift(0))]
	data['check_cross_high'] = data['check_cross_high'].shift(1)
	data['upper_high_cross'] = (data['high'].shift(1))[data['check_cross_high']==data['check_cross_high']]
	data['lower_high_cross'] = (data['low'].shift(1))[data['check_cross_high']==data['check_cross_high']]

	data['upper_high'] = data['upper_high'].fillna(data['upper_high_cross'])
	data['lower_high'] = data['lower_high'].fillna(data['lower_high_cross'])

	data['upper_high'] = data['upper_high'].fillna(method='ffill')
	data['lower_high'] = data['lower_high'].fillna(method='ffill')


	# Swing low:
	data['swing_low'] = (data[close_][(data[low_]<talib.MIN(data[low_], interval).shift(1)) & 
											(data[close_].shift(1) > data[close_].shift(0))  &  
											(data[close_].shift(-1) > data[close_].shift(0))])#.shift(1)
	data['swing_low'] = data['swing_low'].shift(1)

	data['upper_low'] = (data['high'].shift(1))[data['swing_low']==data['swing_low']]
	data['lower_low'] = (data['low'].shift(1))[data['swing_low']==data['swing_low']]
	data['tf_upper_low'] = data['upper_low'].fillna(method='ffill')
	data['tf_lower_low'] = data['lower_low'].fillna(method='ffill')

	data['check_cross_low'] = data[close_][(data[close_] < data['tf_lower_low']) &
										(data[close_].shift(1) > data[close_].shift(0))  &  
											(data[close_].shift(-1) > data[close_].shift(0))]
	data['check_cross_low'] = data['check_cross_low'].shift(1)
	data['upper_low_cross'] = (data['high'].shift(1))[data['check_cross_low']==data['check_cross_low']]
	data['lower_low_cross'] = (data['low'].shift(1))[data['check_cross_low']==data['check_cross_low']]

	data['upper_low'] = data['upper_low'].fillna(data['upper_low_cross'])
	data['lower_low'] = data['lower_low'].fillna(data['lower_low_cross'])

	data['upper_low'] = data['upper_low'].fillna(method='ffill')
	
	data['lower_low'] = data['lower_low'].fillna(method='ffill')
	
	return data[['upper_high', 'lower_high', 'upper_low', 'lower_low']]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO CREATE BASIC SIGNAL BREAK RESISTANCE:
def br_resistance_signal(data_source,interval=10,break_th=0.1,close_='close',open_='open',high_='high',low_='low'):
	data = data_source.copy()

	if type(data) != type(pd.DataFrame()):
		data = pd.DataFrame(data = data, columns = ['close','open','high','low'])

	data[['upper_high', 'lower_high', 'upper_low', 'lower_low']] = sup_res_obs(data,interval=interval,close_=close_,open_=open_,high_=high_,low_=low_)
	data['break_upper'] = data['close']/data['upper_high'] - 1
	sig = data['break_upper'] >= break_th

	sig = np.where( (sig)  & (~sig.shift(1).fillna(False)), True, False)
	# sig =np.reshape(sig, (-1, 4))

	# print(sig)
	return sig

# sup_res_obs(data_source,interval=10,close_='close',open_='open',high_='high',low_='low')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO ADD VOLUME CONDITION:
def add_vol_cond(data_source,sig,vol_inter=10,high_low='high',thrh = 1.5):
	data = data_source.copy()
	data['avr.vol'] = data['volume'].rolling(vol_inter).mean()
	if high_low=='high':
		sig = (sig & (data['volume'] > data['avr.vol']*thrh))
	elif high_low=='low':
		sig = (sig & (data['volume'] < data['avr.vol']/thrh))
	return sig


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO ADD RSI CONDITION:
def add_rsi_cond(data_source,sig,rsi_inter=14,rsi_restrict_low=0,rsi_restrict_high=100):
	data = data_source.copy()
	custom_a = pandas_ta.Strategy(name="First Strategy", ta=[
	{"kind": "rsi", "length": rsi_inter }])
	data.ta.strategy(custom_a)
	sig = (sig & (data['RSI_%d'%rsi_inter] < rsi_restrict_high) & (data['RSI_%d'%rsi_inter] < rsi_restrict_low))
	return sig


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO CHECK LOCAL MAX AND LOCAL MIN:
def check_local_min(data,cond_col,half_left_wing,half_right_wing):
	#mid_point = half_right_wing
	res = pd.DataFrame([True]*len(data),index=data.index)[0]
	for i in range(half_right_wing+1):
		new_cond = (data[cond_col].shift(half_right_wing-i) < data[cond_col].shift(half_right_wing-i-1))
		res = res & new_cond
	for i in range(half_left_wing+1):
		new_cond = (data[cond_col].shift(half_left_wing+i) < data[cond_col].shift(half_left_wing+i+1))
		res = res & new_cond
	return res.shift(half_right_wing)



def check_local_max(data,cond_col,half_left_wing,half_right_wing):
	#mid_point = half_right_wing
	res = pd.DataFrame([True]*len(data),index=data.index)[0]
	for i in range(half_right_wing+1):
		new_cond = (data[cond_col].shift(half_right_wing-i) > data[cond_col].shift(half_right_wing-i-1))
		res = res & new_cond
	for i in range(half_left_wing+1):
		new_cond = (data[cond_col].shift(half_left_wing+i) > data[cond_col].shift(half_left_wing+i+1))
		res = res & new_cond
	return res.shift(half_right_wing)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ADD BREAK AGAIN SIGNAL:
def rebreak(data_source,sig,left_period,right_period,interval=10,price_col='close'):
	data = data_source.copy()
	data[['upper_high', 'lower_high', 'upper_low', 'lower_low']] = sup_res_obs(data,interval=interval)
	# Break again:
	data['local_max'] = data[price_col][check_local_max(data,price_col,half_left_wing=left_period,half_right_wing=right_period)]
	data['local_max'] = data['local_max'].shift(right_period)
	data['local_max'] = data['local_max'].fillna(method='ffill')

	data['higher_local'] = np.where(data['local_max'] > data['local_max'].shift(1), True, 
	                              np.where(data['local_max'] < data['local_max'].shift(1), False, np.nan))
	data['higher_local'] = data['higher_local'].fillna(method='ffill')

	data['higher_break'] = np.where(data['local_max'] > data['upper_high'].shift(1), True, 
	                              np.where(data['local_max'] < data['upper_high'].shift(1), False, np.nan))
	data['higher_break'] = data['higher_break'].fillna(method='ffill')


	# data['sig'] = (data['sig'] & (data['higher_local']))
	sig = (sig & (data['higher_break'].astype(bool)))
	sig = (sig & (data[price_col] > data['local_max'].astype(bool)))

	return sig