
import random 
import string 
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order_book.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)



# datetime symbol order_side order_type price fee 

class Test_Order(db.Model):
	__tablename__ = 'test_orders'
	id = db.Column(db.Integer(), primary_key=True)
	dt = db.Column(db.DateTime())
	symbol = db.Column(db.String(100))
	order_side = db.Column(db.String(100))
	order_type = db.Column(db.String(100))
	amt = db.Column(db.String(100))
	price = db.Column(db.String(100))
	fee = db.Column(db.String(100))


class Live_Order(db.Model):
	__tablename__ = 'live_orders'
	id = db.Column(db.Integer(), primary_key=True)
	dt = db.Column(db.DateTime())
	symbol = db.Column(db.String(100))
	order_side = db.Column(db.String(100))
	order_type = db.Column(db.String(100))
	amt = db.Column(db.String(100))
	price = db.Column(db.String(100))
	fee = db.Column(db.String(100))
	order_id = db.Column(db.String(100))


	
