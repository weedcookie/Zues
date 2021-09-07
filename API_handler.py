### Binance API handler 


import random


from collections import deque
from datetime import datetime , timedelta


from clint.textui import puts , colored


import pandas as pd 


## binance lib by sam 
from binance.client import * 
from binance.enums import * 



## 
from toolkit import *

from mail_order_info import *

from models import db 
from models import Test_Order
from models import Live_Order

from config import sec , pub 




client = Client( pub , sec )


#######################              define class               ########################


class fetch_coin:

	def __init__ (self , coin ):
		''' this create an object for each coin to perform operations on using the methods  '''
		coin_info = client.get_symbol_info(coin)


		sub_dict3 = (coin_info['filters'])[3]
		sub_dict2 = (coin_info['filters'])[2]
		sub_dict  = (coin_info['filters'])[0]

		self.coin = coin 

		#self.balance = 0
		## the average buy and sell prices 
		self.AVG_BUY = 0 
		self.AVG_SELL = 0 

		### this is the que for the sell and buy orders , pop one of each que and calculate profit,fee 
		self.deque_buy = deque()
		self.deque_sell = deque()

		self.test_deque_buy = deque() 
		self.test_deque_sell = deque() 

		## get min max and not values for a single trade
		#  min_not is the smallest order value allowed (amt * price ) = MIN_NOT
		self.MIN_NOT = float()
		self.MIN_QTY = float()
		self.MAX_QTY = float() 


		#self.model = model

		### two lists to hold all buy and sell trades in this session  
		self.buy_lst = [] 
		self.sell_lst = []
		self.ATH = 0
		self.ATL = 0



		self.profit = 0 


    ################################################################
    ################################################################

	def percent_change(self):
		'''returns the change in price in a period of time '''
		res = client.get_ticker(symbol=self.coin)
		self.last_percentChange = float(res['priceChangePercent'])
		return float(res['priceChangePercent'])
    ################################################################
    ################################################################	

	def get_coin_price(self):
		''' get currennt coin price '''
		coin__price = client.get_symbol_ticker(symbol=self.coin)['price']
		return float(coin__price)

    ################################################################
    ################################################################

	def check_balance(self):
		''' check base asset balance '''
		if str(self.balance) == "None":
			print ("       NO FUNDS LEFT !!!! ")
		else:
			print ( "  YOU HAVE " + str(self.balance['free']) +" "+ str(self.balance['asset']))
		try:
			return str(self.balance['free'])
		except TypeError as f:
			return 0

    ################################################################
    ################################################################


	def test_order(self , order_side , order_type ):
		''' create a test order, takes order type  '''

		puts(colored.cyan("Creating a test order of type : {}".format(order_type)))
		## define the trading amount which is 10 times the least allowed amount to trade with
		
		#print (self.MIN_NOT *10 )

		#amt = float(self.MIN_NOT) *10

		amt = 0.3

		if order_type == "LIMIT":

			test_order_info = client.create_test_order(symbol=str(self.coin),
				side=order_side,
    			type=order_type,
    			price=self.get_coin_price(),
    			timeInForce="GTC",
    			quantity=amt)
		else:
			test_order_info = client.create_test_order(symbol=str(self.coin),
				side=order_side,
				type=order_type,
				quantity=amt)


		TEST_DATA = {
		"date_time":f"{datetime.now()}",
		"symbol":f"{self.coin}",
		"order_side":order_side,
		"order_type":order_type,
		"quantity":amt,
		"price":f"{self.get_coin_price()}"}


		if order_side == "SELL":
			self.sell_lst.append(self.get_coin_price())
		
			send_test_order_info(SYMBOL_=self.coin , SIDE_=order_side ,TYPE_=order_type , AMT_=amt ,PRICE_=self.get_coin_price() , PRED_PRICE=TEST_DATA['price'])

			new = Test_Order(dt=datetime.utcnow(),\
							 symbol=self.coin,\
							 order_side=order_side,\
							 order_type=order_type,\
							 amt=amt,\
							 price=self.get_coin_price(),\
							 fee=(float(amt)*float(self.get_coin_price())*0.0075  ))

			db.session.add(new)
			db.session.commit()
			puts(colored.magenta("Added new test order"))
			return TEST_DATA


		elif order_side == "BUY":
			self.buy_lst.append(self.get_coin_price())

			send_test_order_info(SYMBOL_=self.coin , SIDE_=order_side ,TYPE_=order_type , AMT_=amt ,PRICE_=self.get_coin_price() , PRED_PRICE=TEST_DATA['price'])

			new = Test_Order(dt=datetime.utcnow(),\
							 symbol=self.coin,\
							 order_side=order_side,\
							 order_type=order_type,\
							 amt=amt,\
							 price=self.get_coin_price(),\
							 fee=(float(amt)*float(self.get_coin_price())*0.0075  ))

			db.session.add(new)
			db.session.commit()
			puts(colored.magenta("Added new test order"))
			return TEST_DATA

		else:
			return {} 
		

		




    ################################################################
    ################################################################


	def forecast_coin(self):
		"""
		this method fetchs the coinpair performance data 

		returns a dataframe 
		"""

		#### max allowed by binance is 500 data-points 
        #### but you can change the "KLINE_INTERVAL_1MINUTE" check binance docs 
        #### https://python-binance.readthedocs.io/en/latest/binance.html

		puts(colored.blue(f"Fetching data for coin-pair -> {self.coin}"))
		candles = client.get_klines(symbol=str(self.coin),  interval=client.KLINE_INTERVAL_1MINUTE , limit=130)

		date_time = []
		open_lst = []
		high_lst = []
		low_lst = []
		close_lst = []
		volume_lst = []
		for item in candles:
			t_time = float(item[0])/1000
			dt_obj = datetime.fromtimestamp(t_time)
			date_time.append(datetime.fromtimestamp(t_time))
			open_lst.append(float(item[1]))
			high_lst.append(float(item[2]))
			low_lst.append(float(item[3]))
			close_lst.append(float(item[4]))
			volume_lst.append(float(item[5]))
        ## creating data frame 
		coin_data_frame = {
			'date_time' : date_time,
			'open'  : open_lst,
			'high'  : high_lst,
			'low'   : low_lst,
			'close' : close_lst,
			'volume': volume_lst,
			}
		df_ = pd.DataFrame(coin_data_frame , columns = [ 'date_time' , 'open' , 'high' , 'low' , 'close','volume' ])

		rolling_mean = df_['close'].rolling(window=5, min_periods=5 ).mean()
		rolling_mean2 = df_['close'].rolling(window=10, min_periods=10 ).mean()
		df_['5_sma'] = rolling_mean
		df_['10_sma'] = rolling_mean2
		df_.dropna(subset = ["5_sma"], inplace=True)
		df_.dropna(subset = ["10_sma"], inplace=True)
		self.df = df_.tail(120).reset_index(drop=True)



		return self.df 



	def check_orders(self):
		'''  check open orders of coin pair '''

		open_orders_lst = client.get_open_orders(symbol=self.coin)

		return open_orders_lst , len(open_orders_lst)









	def limit_sell_order(self , sell_price):
		''' a method to create a limit order of type sell this order will be open until the 
		current coin price reaches the limit then the order is excuted ''' 


		quant =  self.MIN_QTY *  int (random.randrange(10, 20)) *10

		order = client.order_limit_sell(	
			symbol=self.coin,
			quantity="0.15",
		    timeInForce = "GTC",
			price=sell_price)

		return order 




    ################################################################
    ################################################################

	def limit_buy_order(self , buy_price):
		''' a method to create a limit order of type buy this order will be open until the 
		current coin price reaches the limit then the order is excuted '''
		quant =  self.MIN_QTY *  int (random.randrange(10, 20)) *10

		order = client.order_limit_buy(
			symbol=self.coin,
			quantity="0.15",
			timeInForce = "GTC",
			price=buy_price)

		return order







	def market_BUY(self , amt  ):
		''' the bot executes a BUY with the market price at that moment '''
       
		try:
			buy_order = client.create_order(symbol=self.coin ,type="MARKET" , quantity=str(amt), side="BUY" )
			
			trade_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(buy_order['transactTime']/1000)))
			send_order_info(SYMBOL_=str(self.coin) , TYPE_="BUY" , AMT_=float(amt) , PRICE_=str(buy_order['fills'][0]['price'])  , PRED_PRICE=PRED_PRICE)

			td = {"date_time":str(trade_time),\
			"symbol":str(self.coin),\
			"order_side":"BUY",\
			"order_type":"MARKET",\
			"quantity":amt,\
			"price":float(buy_order['fills'][0]['price']),\
			"fee":float(buy_order['fills'][0]['commission'])}
			return td
            
		except BinanceAPIException as e:
			print (e.status_code)
			return None

	
    
    ################################################################
    ################################################################



	def market_SELL(self , amt  ):
		''' the bot executes a SELL with the market price at that moment '''
       
		try:
			buy_order = client.create_order(symbol=self.coin ,type="MARKET" , quantity=str(amt), side="SELL" )
			
			trade_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(buy_order['transactTime']/1000)))
			send_order_info(SYMBOL_=str(self.coin) , TYPE_="SELL" , AMT_=float(amt) , PRICE_=str(buy_order['fills'][0]['price'])  , PRED_PRICE=PRED_PRICE)

			td = {"date_time":str(trade_time),\
			"symbol":str(self.coin),\
			"order_side":"SELL",\
			"order_type":"MARKET",\
			"quantity":amt,\
			"price":float(buy_order['fills'][0]['price']),\
			"fee":float(buy_order['fills'][0]['commission'])}
			return td
            
		except BinanceAPIException as e:
			print (e.status_code)
			return None





















"""



if __name__ == "__main__":

	clear_screen()
	portfolio = ['BNBBUSD', 'BTCBUSD']#,	'BTCRUB','BNBBTC','BNBETH'] 

	obj_lst = [ fetch_coin(item)  for item in portfolio ] 




	for item in obj_lst:

		response = parse_dataframe(item.forecast_coin() , item.coin)


		item.limit_buy_order(buy_price)
		item.limit_sell_order(sell_price)

		if response == "SELL":
			puts(colored.red("This is a SELL trade "))


		elif response == "BUY":
			puts(colored.green("This is a BUY trade "))

		else:
			puts(colored.yellow("This is a HOLD"))

		puts(colored.blue("\n\n"))

		#item.test_order(order_side="BUY" , order_type="MARKET")



		#read_test_orders()

	print ("\n\n")
	RESULTS = get_symbol('BTCRUB')
	print (f"Found {len(RESULTS)}")

"""

"""

if __name__ == "__main__":
	obj = fetch_coin(coin="BNBBTC")
	obj.forecast_coin()

	parse_dataframe(obj , coinpair=obj.coin)
"""