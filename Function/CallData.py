import pandas as pd

def load_data(folder, name, path):
    #path C:/Users/admin/Dropbox/GitHub/candlestick-screener - VN/FireAnt/EOD/
    file = open(path + folder + '/' + name + '.csv')
    output = pd.read_csv(file)
    return output

a = load_data('Index', 'VNINDEX', 'C:/Users/admin/Dropbox/GitHub/candlestick-screener - VN/FireAnt/EOD/')
print(a)

