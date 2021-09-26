## this is the toolkit file 





import os , random , platform 
from clint.textui import puts , colored , indent 

from datetime import datetime , timedelta 




import matplotlib.dates as mdates
import matplotlib.pyplot as plt 
import matplotlib.transforms as mtransforms 

import pandas as pd 
import numpy as np 


from models import db 
from models import Live_Order 
from models import Test_Order





def clear_screen():
	"""
	clears the screen 
	"""
	try:

		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')
	except :
		puts(colored.red("Encountred an error while clearing the screen !!!!!! "))











def parse_dataframe(obj):
	"""
	takes fetch_coin obj
	"""	


	coinpair = obj.coin

	puts(colored.blue(f"Total data length -> {len(obj.df)}"))



	# list all the close prices 
	close_prices = list(obj.df['close'])
	dt_close_lst = list(obj.df['date_time'])

	# find the slope for the min max incline
	slope = (dt_close_lst[close_prices.index(max(close_prices))].timestamp() - dt_close_lst[close_prices.index(min(close_prices))].timestamp()) / (max(close_prices) - min(close_prices))

	# get the last find values and find the average
	last_five = close_prices[-5:]
	avg_last_five = sum(last_five)/5

	

	# put the info into a dictonary 
	data = {
	"ATH":f"{max(close_prices)}",
	"ATL":f"{min(close_prices)}",
	"AVG":f"{sum(close_prices)/len(close_prices)}",
	"AVG_5":avg_last_five,
	"slope":f"{slope}"}

	# check if all time high or low is recorded  
	if not obj.ATH :
		obj.ATH = float(data['ATH'])
	elif float(data['ATH']) > obj.ATH:
		obj.ATH = float(data['ATH'])

	if not obj.ATL :
		obj.ATL = float(data['ATL'])
	elif float(data['ATL']) < obj.ATL:
		obj.ATL = float(data['ATL'])

	current = obj.get_coin_price() 
	if current > max(close_prices):
		data['ATH'] = float(current)
	elif current < min(close_prices):
		data['ATL'] = float(current)



	puts(colored.yellow(f"ATH : {obj.ATH} ATL : {obj.ATL} Current : {current}"))

	avg_list = [ float(data['AVG']) for i in range(len(dt_close_lst)) ] 

	#print (df.head(3))
	#print (df.tail(3))
	#print (data)


	## drawing the graph 
	plt.rcParams['axes.facecolor'] = 'grey'
	plt.grid(color='black')
	plt.plot(dt_close_lst , close_prices , color='black', label="close_prices")
	
	plt.plot(dt_close_lst , list(obj.df['5_sma']) , color='magenta' , label="5_SMA" )
	plt.plot(dt_close_lst , avg_list  , color='white' , label="AVG" )


	plt.scatter(dt_close_lst[close_prices.index(max(close_prices))] , max(close_prices), color='cyan' , label = "max close price")
	plt.scatter(dt_close_lst[close_prices.index(min(close_prices))] , min(close_prices), color='yellow' , label = "min close price")
	plt.legend()
	plt.savefig(coinpair+".png")
	#plt.show(block=False)
	#plt.pause(3)
	#plt.close()
	plt.clf()
	
	#plt.show()


	# find the ratio between the average and last five values 

	x = round(( (avg_last_five / float(data['AVG'])) -1  )*100 , 4)
	y = round(( (float(data['AVG']) / avg_last_five)  -1  )*100, 4)

	print (x, y)



	if x > .3 and current >  float(data['AVG']) :
		puts(colored.red("This is a SELL trade"))
		return "SELL"
	elif y > .3 and current < float(data['AVG']) :
		puts(colored.green("This is a BUY trade"))
		return "BUY"
	else:
		puts(colored.yellow("This is a HOLD"))
		return "HOLD"





def check_point(obj , order_side ):

	print (f"BUY->{obj.buy_lst}")
	print (f"SELL->{obj.sell_lst}")

###### SELL section
	if order_side == "SELL" and not obj.sell_lst:
		return True
	elif order_side == "SELL" and obj.sell_lst :
		if ( obj.get_coin_price() / max(obj.sell_lst) ) >  1.002 :

			return True
		else:
			return False

###### BUY section
	if order_side == "BUY" and not obj.buy_lst:
		return True
	elif order_side == "BUY" and obj.buy_lst:
		if (min(obj.buy_lst) / obj.get_coin_price()) > 1.002:
			return True
		else:
			return False

	


def sell_ratio(obj):
	"""
	this function returns the change in sell 
	"""
	if obj.sell_lst:
		min_ = min(obj.sell_lst)
		max_ = max(obj.sell_lst)
		ratio_sell = round((max_/min_), 3 )
		print (f"Max:Min SELL {ratio_sell}")
		return ratio_sell


def buy_ratio(obj):
	"""
	this function returns the change in sell 
	"""
	if obj.buy_lst:
		min_ = min(obj.buy_lst)
		max_ = max(obj.buy_lst)
		ratio_buy = round((max_/min_), 3 )
		print (f"Max:Min BUY {ratio_buy}")

		return ratio_buy






def order_span(obj ):

	"""
	check the ratio between the highest and lowest order price for buy and sell 
	"""

	MAX_SELL = max(obj.sell_lst)
	MIN_SELL = min(obj.sell_lst)

	
	MAX_BUY = max(obj.buy_lst)
	MIN_BUY = min(obj.buy_lst)

	return MAX_SELL/MIN_SELL ,  MAX_BUY/MIN_BUY







def all_trades(lst):
	buys = []
	sells = [] 
	buy_shares = 0 
	sell_shares = 0 


	for item in lst:
		if item.order_side == "BUY":
			buys.append(item)
			buy_shares += float(item.amt)

		elif item.order_side == "SELL":
			sell_shares += float(item.amt)
			sells.append(item)


	
	return buys , sells , [ buy_shares , sell_shares]



def all_buys(symbol, order_type , test):

	if test == True:
		all_buys = Test_Order.query.filter_by(symbol=symbol , order_type=order_type, order_side="BUY").all()
	elif test == False:
		all_buys = Live_Order.query.filter_by(symbol=symbol , order_type=order_type, order_side="BUY").all()	

	return all_buys


def all_sells(symbol , order_type , test):

	if test == True:

		all_sells = Test_Order.query.filter_by(symbol=symbol , order_type=order_type , order_side="SELL").all()
	elif test == False:
		all_sells = Live_Order.query.filter_by(symbol=symbol , order_type=order_type , order_side="SELL").all()

	return all_sells



def prof_filter(buy_lst , sell_lst):
	if len(buy_lst) > len(sell_lst) :
		k = len(sell_lst)
		
	
	elif len(sell_lst) > len(buy_lst) :
		k = len(buy_lst)
	
	else:
		k=0
	


	cash = 0 

	
	for buy in  buy_lst[:k]:
		cash -= float(buy.amt) * float(buy.price)
		#del buy_lst[buy_lst.index(buy)]

	for sell in sell_lst[:k]:
		cash += float(sell.amt) * float(sell.price)
		#del sell_lst[sell_lst.index(sell)]

	

	print (f"Total profit : {cash}")
	print (f"Left trades ---> BUYS :[{len(buy_lst[k:])}] SELLS :[{len(sell_lst[k:])}]")


	tmp = [] 

	if len(buy_lst[k:]) > len(sell_lst[k:]) :
		for item in buy_lst[k:] :
			tmp.append(item)

		z = "BUY" 

	elif len(buy_lst[k:]) < len(sell_lst[k:]) :
		for item in sell_lst[k:] :
			tmp.append(item)		
		z = "SELL"

	# price lst 
	plst = [ item.price for item in tmp ]

	if len(plst) != 0:
		print (f" Max {max(plst)} : Min {min(plst)}")

	return tmp, plst






#clear_screen()
