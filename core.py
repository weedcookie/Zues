

import os , random , sys , time 

from clint.textui import puts , colored 
from datetime import datetime , timedelta

import config
from toolkit import *
from API_handler import *

from models import db 
from models import Test_Order
from models import Live_Order 



n = 0 


def check_db():

	if os.path.exists(os.getcwd() +"/order_book.db") :
		puts(colored.blue("Found database file."))
	else:
		puts(colored.red("Database file not found or is located in the wrong place."))	
		puts(colored.blue("Creating new database file."))
		db.create_all()
	return True

















## contains objects of fetch_coin class 
obj_list = [ fetch_coin(item) for item in config.portfolio ] 



def intro(obj):
	"""
	"""

	print ("\n")	
	open_lst , n_orders = obj.check_orders()

	#puts(colored.cyan(f"{n_orders} open orders"))
	
	obj.forecast_coin()

	response = parse_dataframe(obj  )



	state = check_point(obj ,response)

	## create a test order and records the price for that trade 

	if response == "SELL" and state == True:
		obj.test_order(order_side="SELL" , order_type="LIMIT")
	elif response == "BUY" and state == True:
		obj.test_order(order_side="BUY" , order_type="LIMIT")

	if obj.sell_lst:
		SELL_RATIO = sell_ratio(obj)
		if SELL_RATIO > 1.03 and response == "SELL":
			puts(colored.red(F"THIS IS A SELL TRADE ......................... {obj.get_coin_price()} "))
	
	if obj.buy_lst:
		BUY_RATIO = buy_ratio(obj)
		if BUY_RATIO > 1.3 and response == "BUY":
			puts(colored.green(F"THIS IS A BUY TRADE .......................... {obj.get_coin_price()}"))
	

	








	#puts(colored.cyan("Moving to the next coinpair "))
	puts(colored.cyan("______________________________________________________________"))






















if __name__ == "__main__":
	check_db()
	time.sleep(3)
	clear_screen()
	puts(colored.cyan(config.banner))

	ini_time_for_now = datetime.now()
	print ("initial_date", str(ini_time_for_now))
	while True :
		
	
		next_checkpoint = ini_time_for_now + timedelta(seconds=30)

		if datetime.now().timestamp() > next_checkpoint.timestamp():

			try:
				clear_screen()
				for item in obj_list:
				
					
						intro(item)
					 
					
					
				n += 1
				print ("\n")
				print (f"Iteration number [{n}] ")

			except requests.exceptions.Timeout as Time_out  :
				print (f"Time out encountered\n {Time_out}")
				time.sleep(120)
			except requests.exceptions.ConnectionError as binance_error_2:
				print (binance_error_2)
				time.sleep(120)
			
			ini_time_for_now = datetime.now()
			print ("initial_date", str(ini_time_for_now))
			