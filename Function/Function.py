import pandas as pd
import numpy as np
#===============================================================================================================
#Slope
def check_trend_line(support: bool, pivot: int, slope: float, y: np.array):
    # compute sum of differences between line and prices, 
    # return negative val if invalid 
    
    # Find the intercept of the line going through pivot point with given slope
    intercept = -slope * pivot + y[pivot]
    line_vals = slope * np.arange(len(y)) + intercept
     
    diffs = line_vals - y
    
    # Check to see if the line is valid, return -1 if it is not valid.
    if support and diffs.max() > 1e-5:
        return -1.0
    elif not support and diffs.min() < -1e-5:
        return -1.0

    # Squared sum of diffs between data and line 
    err = (diffs ** 2.0).sum()
    return err;

def optimize_slope(support: bool, pivot:int , init_slope: float, y: np.array):
    
    # Amount to change slope by. Multiplyed by opt_step
    slope_unit = (y.max() - y.min()) / len(y) 
    
    # Optmization variables
    opt_step = 1.0
    min_step = 0.0001
    curr_step = opt_step # current step
    
    # Initiate at the slope of the line of best fit
    best_slope = init_slope
    best_err = check_trend_line(support, pivot, init_slope, y)
    assert(best_err >= 0.0) # Shouldn't ever fail with initial slope

    get_derivative = True
    derivative = None
    while curr_step > min_step:

        if get_derivative:
            # Numerical differentiation, increase slope by very small amount
            # to see if error increases/decreases. 
            # Gives us the direction to change slope.
            slope_change = best_slope + slope_unit * min_step
            test_err = check_trend_line(support, pivot, slope_change, y)
            derivative = test_err - best_err;
            
            # If increasing by a small amount fails, 
            # try decreasing by a small amount
            if test_err < 0.0:
                slope_change = best_slope - slope_unit * min_step
                test_err = check_trend_line(support, pivot, slope_change, y)
                derivative = best_err - test_err

            if test_err < 0.0: # Derivative failed, give up
                raise Exception("Derivative failed. Check your data. ")

            get_derivative = False

        if derivative > 0.0: # Increasing slope increased error
            test_slope = best_slope - slope_unit * curr_step
        else: # Increasing slope decreased error
            test_slope = best_slope + slope_unit * curr_step
        

        test_err = check_trend_line(support, pivot, test_slope, y)
        if test_err < 0 or test_err >= best_err: 
            # slope failed/didn't reduce error
            curr_step *= 0.5 # Reduce step size
        else: # test slope reduced error
            best_err = test_err 
            best_slope = test_slope
            get_derivative = True # Recompute derivative
    
    # Optimize done, return best slope and intercept
    return (best_slope, -best_slope * pivot + y[pivot])
def fit_trendlines_single(data: np.array):
    # find line of best fit (least squared) 
    # coefs[0] = slope,  coefs[1] = intercept 
    x = np.arange(len(data))
    coefs = np.polyfit(x, data, 1)

    # Get points of line.
    line_points = coefs[0] * x + coefs[1]

    # Find upper and lower pivot points
    upper_pivot = (data - line_points).argmax() 
    lower_pivot = (data - line_points).argmin() 
   
    # Optimize the slope for both trend lines
    support_coefs = optimize_slope(True, lower_pivot, coefs[0], data)
    resist_coefs = optimize_slope(False, upper_pivot, coefs[0], data)

    return (support_coefs, resist_coefs) 
# Slope                 ##a = slope(df, 10, "close")
def slope(data, lookback, columns):  
    data= df
    support_slope = pd.DataFrame()
    support_slope = [fit_trendlines_single(data.iloc[i - lookback + 1: i + 1][columns])[0][0] for i in range(lookback - 1, len(data))]
    
    data["support_slope"] = [np.nan] * len(data)
    data.loc[lookback-1:,'support_slope'] = support_slope 
    answer = data['support_slope'].to_numpy()
    answer = np.arctan(data['support_slope'])
    answer1 = np.degrees(answer)
    answer1 = answer1.dropna()
    return answer1


#=========================================================================================================
#Call Data Stock FireAnt

def load_data(path, folder, name):
    file = open(path + '/' + folder + '/' + name + '.csv')
    output = pd.read_csv(file)
    return output
#a = load_data('Index', 'VNINDEX', 'C:/Users/admin/Dropbox/GitHub/candlestick-screener - VN/FireAnt/EOD/')
#print(a)



#=============================================================================================================
#Call Intraday Data Stock FireAnt

#input_path_custom_data = 'C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/EOD/Stock/'

#Load data Intraday FireAnt    #load_data('C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Intraday',"Stock",'FPT',"1T")  #Time: 1T = 1 min
#input_path_fireant = 'C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Intraday'
def load_data_intradayfa(input_path_fireant,folder,stock,time):

    file = open(input_path_fireant +'/' + folder + '/'+ stock + '.csv')
    df_f = pd.read_csv(file)
    df_f['time'] = pd.to_datetime(df_f['datetime']+ ' ' + df_f['time'])
    df_f1 = df_f.groupby([pd.Grouper(key='time', freq= time)])\
        .agg(open=pd.NamedAgg(column='Open', aggfunc='first'), 
             close=pd.NamedAgg(column='Open', aggfunc='last'), 
             high=pd.NamedAgg(column='Open', aggfunc='max'), 
             low=pd.NamedAgg(column='Open', aggfunc='min'),
             volume=pd.NamedAgg(column='volume', aggfunc='sum'))\
    .reset_index()
    df_f1 = df_f1.dropna()
    return df_f1

#===========================================================================================================
#Load data stock from TradingView 30min
#input_path_small_interval =     
def load_small_interval(input_path_small_interval,stock,time):
    fileTV  = open(input_path_small_interval + '/' + stock + '.csv')
    df_f = pd.read_csv(fileTV)
    df_f['datetime'] = pd.to_datetime(df_f['datetime'])
    df_f1 = df_f.groupby([pd.Grouper(key='datetime', freq= time)])\
        .agg(open=pd.NamedAgg(column='open', aggfunc='first'), 
             close=pd.NamedAgg(column='close', aggfunc='last'), 
             high=pd.NamedAgg(column='high', aggfunc='max'), 
             low=pd.NamedAgg(column='low', aggfunc='min'),
             volume=pd.NamedAgg(column='volume', aggfunc='sum'))\
    .reset_index()
    df_f1 = df_f1.dropna()
    return df_f1

#=================================================================================================================
# Add custom data stock from EOD FireAnt to Data Tradingview (Data 1 day, time = "1d")
#df = add_custom_data("C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Tradingview data/4hvn", "C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/EOD/Stock", "FPT","1d")

def add_custom_data(input_path_data_1,input_path_custom_data,stock):
    data_small_interval = load_small_interval(input_path_data_1,stock,"1d")
    data_small_interval['date']= [x.date() for x in data_small_interval['datetime']]
    fileFireAnt = open(input_path_custom_data + '/' + stock + '.csv')
    df_f0 = pd.read_csv(fileFireAnt)
    df_f0['datetime'] = pd.to_datetime(df_f0['datetime'])
    df_f0['date']= [x.date() for x in df_f0['datetime']]
    df_f0 = df_f0.drop(columns = ['open','high','low','SL luu hanh','symbol'])
    df = pd.merge(data_small_interval, df_f0, how = "inner", on="date")
    df = df.drop(columns = ['date','datetime_y'])
    df = df.rename(columns={"datetime_x":"datetime","close_x": "close","volume_x": "volume","close_y": "close EOD","volume_y":"volume EOD"})
    df = df[["datetime","open","high","low","close","volume","close EOD","volume EOD"]]
    return df

#===================================================================================================================
#Holding Period   

def holding_period(entries):
    df2 = pd.DataFrame(entries).reset_index()
    df2 = df2.set_axis(['datetime','entry'], axis = 1, inplace =False)
    df2['pos'] = pd.Series(dtype=float)
    df2['close'] = pd.DataFrame(df['close'].values)
    for a in df2.index:
        if df2["entry"][a] == True:
            df2["pos"][a] =1
    df2[["pos_shift"]] = df2[["pos"]].shift(1)
    df2["check_entry"] = df2["datetime"][(~df2["pos"].isna()) & (df2["pos_shift"].isna())]
    df2["check_entry"] = df2["check_entry"].fillna(method = "ffill")
    df2["holding"] = df2["datetime"] - df2["check_entry"]
    df2["check_price"] = df2["close"][(~df2["pos"].isna()) & (df2["pos_shift"].isna())]
    df2["check_price"] = df2["check_price"].fillna(method = "ffill")
    df2 = df2.drop(columns =["pos","pos_shift","check_entry"])
    df2['return'] = (df2['close']-df2['check_price'])/(df2['check_price'])
    df2= df2.drop(columns = ['check_price'])
    df2 = df2.dropna()
    return df2
