import pandas as pd


def resample(data,resampl_inter='30min',**kwargs):

	if len(kwargs)==0:
		ohlc_dict = {
			'open':'first',
			'high':'max',
			'low':'min',
			'close':'last',
			'volume':'sum'
			}
	else:
		ohlc_dict = dict()

	if len(kwargs)!=0:
		ohlc_dict.update(kwargs)


	res_data = data.resample(resampl_inter).agg(ohlc_dict)
	res_data.dropna(subset=[res_data.columns[0]],inplace=True)
	return res_data

