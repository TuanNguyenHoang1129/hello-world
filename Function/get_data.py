from datetime import datetime
import pymongo
import certifi
import pandas as pd
from pymongo import MongoClient
from bson import Code


def get_client():
	return pymongo.MongoClient("mongodb+srv://hodinhtan:HFhtuT5RfgPBDjEn@cluster0.yvr1go5.mongodb.net/?retryWrites=true&w=majority", 
		tlsCAFile=certifi.where())


def get_datbase(mongo_client,data_source='metastock'):
	return mongo_client['data'][data_source]


def info_data(mongo_data):
	document = mongo_data.find_one()
	all_cols = [k for k in document]
	return all_cols

def detail_info(mongo_data,info_need,**kwargs):
	# kwargs = kwargs['kwargs']
	querry  = kwargs
	# data = mongo_data.find(querry)
	all_assets = mongo_data.distinct(info_need,querry)
	return all_assets


def check_volume(mongo_data,n_days,low_limit=0,high_limit=100000000000,**kwargs):

	found_condition = list(mongo_data.aggregate([
   {
      '$match': {
         '$expr': {
            '$gte': ["$time", {'$subtract': ["$$NOW", n_days*60*60*24*1000]}]}}},
   
   {'$match': {'type': 'EOD',
   				'kind':'stock'}},

   {"$group": {
         '_id': {"symbol": "$symbol", 
             "type": "$type", 
             "kind": "$kind",
             "marketdivision":"$marketdivision"},
         "volume": {
            "$avg": "$volume"}}},

   {'$match': {'volume': {'$gte':low_limit, "$lte" : high_limit}}},


   {'$group':{'_id':'$_id.symbol', 'symbol':{'$first':'$_id.symbol'}}},

   { "$sort" : {"_id" : 1}}

   ]))
	return pd.DataFrame(found_condition)['_id'].to_list()



def fetch_trading(symbol,mongo_data,interval='1D',exchange='HOSE',start='2000/01/01',stop='now',**kwargs):
	start  = datetime.strptime(start,'%Y/%m/%d')
	if stop == 'now':
		end = datetime.now()
	else:
		end = datetime.strptime(stop,'%Y/%m/%d')
	
	querry  = {"exchange": exchange, "symbol": symbol, 'interval': interval, "time" : {'$lt': end, '$gte': start}} 
	if len(kwargs)!=0:
		querry.update(kwargs)
	index_lis = [(k,pymongo.ASCENDING) for k in querry.keys()]
	mongo_data.create_index(index_lis)
	


	data = mongo_data.find(querry)
	columns = ['time', 'open', 'high', 'low', 'close', 'volume']

	results = pd.DataFrame(data=data,columns=columns)
	results.rename(columns={'time':'datetime'},inplace=True)
	results = results.set_index('datetime')

	if interval == '1D':
		results.set_index(results.index.date,inplace=True)
	return results


def fetch_meta(symbol,mongo_data,type_='EOD', kind='stock', marketdivision='',start='2000/01/01',stop='now',**kwargs):
	start  = datetime.strptime(start,'%Y/%m/%d')
	if stop == 'now':
		end = datetime.now()
	else:
		end = datetime.strptime(stop,'%Y/%m/%d')


	if kind == 'market':
		if marketdivision == 'AC':
			mdict = {"time":"time","open":"mactsell","close":"mactbuy","high":"mmax","low":"mmin","volume":"msellorder","oi":"mbuyorder"}
		elif marketdivision=='CC':
			mdict = {"time":"time","open":"mssell","close":"msbuy","high":"mmax","low":"mmin","volume":"msellorder","oi":"mbuyorder"}
		elif marketdivision=='TD':
			mdict = {"time":"time","open":"mpsell","close":"mpbuy","high":"mmax","low":"mmin","volume":"msellval","oi":"mbuyval"}
		elif marketdivision=='NN':
			mdict = {"time":"time","open":"mfsell","close":"mfbuy","high":"mmax","low":"mmin","volume":"msellval","oi":"mbuyval"}
	else:
		mdict = {"time":"time","open":"open","close":"close","high":"high","low":"low","volume":"volume","oi":"oi"}



	name_dict = {"stock":{"time":"time","open":"open","high":"high","low":"low","close":"close","volume":"volume","oi":"float"},
	"active":{"time":"time","open":"actsell","close":"actbuy","high":"amax","low":"amin","volume":"asellorder","oi":"abuyorder"},
	"foreign":{"time":"time","open":"fsell","close":"fbuy","high":"fmax","low":"fmin","volume":"fsellval","oi":"fbuyval"},
	"supplydemand":{"time":"time","open":"actsell","close":"actbuy","high":"smax","low":"smin","volume":"ssellorder","oi":"sbuyorder"},
	"prop":{"time":"time","open":"psell","close":"pbuy","high":"pmax","low":"pmin","volume":"psellval","oi":"pbuyval"},
	"futures":{"time":"time","open":"open","close":"close","high":"high","low":"low","volume":"volume","oi":"ftransval"},
	"index":{"time":"time","open":"open","close":"close","high":"high","low":"low","volume":"volume","oi":"float"},
	"industry":{"time":"time","open":"open","close":"close","high":"high","low":"low","volume":"volume"},
	'warrant':{"time":"time","open":"open","high":"high","low":"low","close":"close","volume":"volume","oi":"float"},
	"market":mdict}


	querry  = {"type" : type_,   'kind': kind ,  'marketdivision':marketdivision, "symbol": symbol, "time" : {'$lt': end, '$gte': start}}
	if len(kwargs)!=0:
		querry.update(kwargs)
	index_lis = [(k,pymongo.ASCENDING) for k in querry.keys()]
	mongo_data.create_index(index_lis)

	data = mongo_data.find(querry)
	columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'oi']


	results = pd.DataFrame(data=data,columns=columns)
	results.set_index('time',inplace=True)
	results.rename(columns=name_dict[kind],inplace=True)
	columns = list(name_dict[kind].values())
	columns.remove("time")
	results = results[columns]

	return results




def columns_meaning(kind,marketdivision=''):
	if kind == 'market':
		if marketdivision == 'AC':
			mdict = {"time":"timestamp","mactsell":"SellVolume","close":"BuyVolume","mmax":"Max(sell,buy)","mmin":"Min(sell,buy)",
			"msellorder":"number_of_sell_orders","mbuyorder":"number_of_buy_orders"}
		elif marketdivision=='CC':
			mdict = {"time":"timestamp","mssell":"SellVolume","msbuy":"BuyVolume","mmax":"Max(sell,buy)",
			"mmin":"Max(sell,buy)","msellorder":"number_of_sell_orders","mbuyorder":"number_of_buy_orders"}
		elif marketdivision=='TD':
			mdict = {"time":"timestamp","mpsell":"SellVolume","mpbuy":"BuyVolume","mmax":"Max(sell,buy)",
			"mmin":"Max(sell,buy)","msellval":"sell_value","oi":"buy_value"}
		elif marketdivision=='NN':
			mdict = {"time":"timestamp","mfsell":"SellVolume","mfbuy":"BuyVolume","mmax":"Max(sell,buy)",
			"mmin":"Min(sell,buy)","msellval":"sell_value","mbuyval":"buy_value"}
	else: mdict = {}

	name_dict = {"stock":{"time":"timestamp","open":"open","high":"high","low":"low","close":"close","volume":"volume","float":"number_of_floats"},

	"active":{"time":"timestamp","actsell":"SellVolume","close":"BuyVolume","amax":"Max(sell,buy)",
	"amin":"Min(sell,buy)","asellorder":"number_of_sell_orders","abuyorder":"number_of_buy_orders"},

	"foreign":{"time":"timestamp","fsell":"SellVolume","fbuy":"BuyVolume","fmax":"Max(sell,buy)",
	"fmin":"Min(sell,buy)","fsellval":"sell_value","fbuyval":"buy_value"},

	"supplydemand":{"time":"timestamp","actsell":"SellVolume","actbuy":"BuyVolume","smax":"Max(sell,buy)",
	"smin":"Min(sell,buy)","ssellorder":"number_of_sell_orders","sbuyorder":"number_of_buy_orders"},

	"prop":{"time":"timestamp","psell":"SellVolume","pbuy":"BuyVolume","pmax":"Max(sell,buy)",
	"pmin":"Min(sell,buy)","psellval":"sell_value","pbuyval":"buy_value"},

	"futures":{"time":"timestamp","open":"open","close":"close","high":"high",
	"low":"low","volume":"volume","ftransval":"total_transaction_value"},

	"index":{"time":"timestamp","open":"open","close":"close","high":"high",
	"low":"low","volume":"volume","float":"number_of_floats"},

	"industry":{"time":"timestamp","open":"open","close":"close","high":"high",
	"low":"low","volume":"volume"},

	'warrant':{"time":"time","open":"open","high":"high","low":"low","close":"close","volume":"volume","float":"number_of_issued_warrant"},

	"market":mdict}

	df = pd.DataFrame({k:[v] for k,v in name_dict[kind].items()})
	return df