# import warnings
# warnings.filterwarnings('ignore')

# import numpy as np
# import pandas as pd
# import vectorbt as vbt

# import Testing
# import Sup_Res_Duc
# import pandas as pd
# import os



# # np.random.seed(42)
# df = pd.read_csv(r"C:\Users\hp\Dropbox\FireAnt\EOD\Stock\A32.csv")



# intervals=np.arange(5, 21, 5),
# break_ths=np.arange(0.05, 0.8, 0.05)



# # data_source,interval=10,close_='close',open_='open',high_='high',low_='low'
# # br_resistance_signal(data_source,interval=10,break_th=0.1,close_='close',open_='open',high_='high',low_='low')

# my_indicator = vbt.IndicatorFactory(
# 	class_name="Sup_Res_Duc.br_resistance_signal",
# 	short_name="SupRes",
# 	input_names=["data_source"],
# 	param_names=["interval","break_th","close_","open_","high_","low_"],
# 	output_names=["sig"]
# 	).from_apply_func(
# 	Sup_Res_Duc.br_resistance_signal,
# 	interval=10,
# 	break_th=0.1,
# 	close_='close',
# 	open_='open',
# 	high_='high',
# 	low_='low')

# sig = my_indicator.run(
#     df[['close','open','high','low']],
#     interval=10,
# 	break_th=0.1,
# 	close_='close',
# 	open_='open',
# 	high_='high',
# 	low_='low')

# print(sig)




import vectorbt as vbt
import numpy as np
import pandas as pd
from numba import njit
from datetime import datetime
import talib as ta

price = pd.DataFrame({
    'a': [1, 2, 3, 4, 5],
    'b': [5, 4, 3, 2, 1]
}, index=pd.Index([
    datetime(2020, 1, 1),
    datetime(2020, 1, 2),
    datetime(2020, 1, 3),
    datetime(2020, 1, 4),
    datetime(2020, 1, 5),
])).astype(float)

print(price)

def rsi_signals_indicator(close, length = 14, ob_level = 70, os_level=30):
    rsi = ta.RSI(close, length)
 
    long_signals  = np.where(np.logical_and(pd.Series(rsi).shift(1) < os_level, rsi >= os_level), 1, 0)
    short_signals = np.where(np.logical_and(pd.Series(rsi).shift(1) > ob_level, rsi <= ob_level), 1, 0)
 
    return long_signals,short_signals


RSI_indicator = vbt.IndicatorFactory(
    class_name="RSI Indicator",
    short_name="RSI Ind",
    input_names=["close"],
    param_names=["length","ob_level","os_level"],
    output_names=["long_signals","short_signals"]
).from_apply_func(
    rsi_signals_indicator,
    length   = 14,
    ob_level = 70,
    os_level = 30,
    to_2d = False
)


length_arr   = np.arange(10,20)
os_level_arr = np.arange(20,30)
ob_level_arr = np.arange(70,80)



ind_grid = RSI_indicator.run(
    price.a, 
    length    = length_arr,
    ob_level  = ob_level_arr, 
    os_level  = os_level_arr, 
    param_product = True)


print(ind_grid)






# import numpy as np
# from sklearn.model_selection import ParameterGrid

# # Load the data
# close = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

# # Define the parameter grid
# param_grid = {'short_ma': range(2, 6),
#               'long_ma': range(6, 11)}

# # Define the scoring function
# def score_function(close, short_ma, long_ma):
#     short_ma_vals = np.convolve(close, np.ones(short_ma)/short_ma, mode='valid')
#     long_ma_vals = np.convolve(close, np.ones(long_ma)/long_ma, mode='valid')
#     signal = np.where(short_ma_vals > long_ma_vals, 1, 0)
#     return signal[-1]  # Use the last signal value as the score



# print(list(ParameterGrid(param_grid)))


# # # Perform grid search
# # best_score = -np.inf
# # for params in ParameterGrid(param_grid):
# #     score = score_function(close, **params)
# #     if score > best_score:
# #         best_score = score
# #         best_params = params

# # print(f"Best parameters: {best_params}")
# # print(f"Best score: {best_score}")

