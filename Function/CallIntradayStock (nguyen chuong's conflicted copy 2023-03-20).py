import pandas as pd

def load_data(folder,stock,time):

    file =  file = open('C:/Users/Nguyen Quang Bac/Dropbox/FireAnt/Intraday/' + folder + '/' + stock + '.csv')
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
c = load_data("Futures","VN30F1M","1T")  #Time: 1T = 1 min
print(c)


