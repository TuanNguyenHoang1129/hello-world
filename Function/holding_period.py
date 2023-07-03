import pandas as pd
import numpy as np
path = "C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/EOD"
def load_data(path, folder, name):
    file = open(path + '/' + folder + '/' + name + '.csv')
    output = pd.read_csv(file)
    return output


def load_data_intradayFA(input_path_fireant,folder,stock,time):

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

def holding_period(entries):
    df1 = pd.DataFrame(entries).reset_index()
    df1 = df1.set_axis(['datetime','entry'], axis = 1, inplace =False)
    df1['pos'] = pd.Series(dtype=float)
    for a in df1.index:
        if df1["entry"][a] == True:
            df1["pos"][a] =1
    df1[["pos_shift"]] = df1[["pos"]].shift(1)
    df1["check_entry"] = df1["datetime"][(~df1["pos"].isna()) & (df1["pos_shift"].isna())]
    df1["check_entry"] = df1["check_entry"].fillna(method = "ffill")
    df1["holding"] = df1["datetime"] - df1["check_entry"]
    df1 = df1.drop(columns =["pos","pos_shift","check_entry"])
    returns= df["close"].pct_change()
    df1["return"] =  df["close"].pct_change().values
    df1 = df1.dropna()
    return df1

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
#df1 = add_custom_data("C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Tradingview data/4hvn", "C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/EOD/Stock", "FPT")

