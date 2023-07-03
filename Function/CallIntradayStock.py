import pandas as pd

input_path_small_interval = 'C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Tradingview Data/'
input_path_custom_data = 'C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/EOD/Stock/'

#Load data Intraday FireAnt    #load_data("Futures","VN30F1M","1T")  #Time: 1T = 1 min
def load_data(folder,stock,time):

    file = open('C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Intraday/' + folder + '/' + stock + '.csv')
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
#Load data from TradingView 30min
def load_small_interval(stock,time):
    fileTV  = open(input_path_small_interval + stock + '.csv')
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
# Add custom data
def add_custom_data(stock,time):
    data_small_interval = load_small_interval(stock,time)
    data_small_interval['date']= [x.date() for x in data_small_interval['datetime']]
    fileFireAnt = open(input_path_custom_data + stock + '.csv')
    df_f0 = pd.read_csv(fileFireAnt)
    df_f0['datetime'] = pd.to_datetime(df_f0['datetime'])
    df_f0['date']= [x.date() for x in df_f0['datetime']]
    df_f0 = df_f0.drop(columns = ['open','high','low','SL luu hanh','symbol'])
    df = pd.merge(data_small_interval, df_f0, how = "inner", on="date")
    df = df.drop(columns = ['date','datetime_y'])
    df = df.rename(columns={"datetime_x":"datetime","close_x": "close","volume_x": "volume","close_y": "close EOD","volume_y":"volume EOD"})
    df = df[["datetime","open","high","low","close","volume","close EOD","volume EOD"]]
    return df