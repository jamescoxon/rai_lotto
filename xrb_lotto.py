from flask import Flask
from flask import render_template, redirect, url_for, request, abort, flash, session
import requests
import threading
import settings
import time
import json
from random import randint
from tinydb import TinyDB, Query

db = TinyDB('db.json')

import pickle
object = {'addresses' : '', 'funds' : 0}
f = open('store.pckl', 'wb')
pickle.dump(object, f)
f.close()

id_key = settings.id_key
fund_address = settings.fund_address
draw_gap = 60 * 60

app = Flask(__name__)

def lotto_loop():
	print('Run Lotto')
	addresses = []
	#Check that there is actually a fund:
	r = requests.post('http://yapraiwallet.space:5000/get_balance', data = {'id_key': id_key, 'address' : fund_address})
	total_fund = int(r.json()['rai'])
	#Get Contestents
	result = db.all()
	total_num = len(result) - 1
	last_block = result[total_num]['last_block']

	if total_fund > 0:
		r = requests.post('http://yapraiwallet.space:5000/get_history', data = {'id_key': id_key, 'address' : fund_address, 'count' : 50, 'filter' : last_block})
		for contestents in r.json()['history']:
			if contestents['type'] == 'receive' and contestents['rai'] >= 1000000:
				#print (contestents['account'])
				addresses.append(contestents['account'])

		#Select Winner
		print("Address: ")
		print(addresses)
		if len(addresses) > 0:
			print("Got addresses to do a draw")
			draw = randint(0, (len(addresses) -1))
			print('Draw: %d, Range: 0 - %d' % (draw, (len(addresses) -1)))
			print('WINNER: %s' % addresses[draw])
			winner = addresses[draw]
			#Pay Winner
			#Send
			r = requests.post('http://yapraiwallet.space:5000/send', data = {'id_key': id_key, 'from_address' : fund_address, 'to_address' : winner, 'rai' : total_fund })
			print(r.json())
		else:
			print("No addresses - just wait")
			winner = 'None'

		#Setup next Draw
		r = requests.post('http://yapraiwallet.space:5000/get_history', data = {'id_key': id_key, 'address' : fund_address, 'count' : 1, 'filter' : 0})
		print('Request return: ')
		print(r.json())
		last_block = r.json()['history'][0]['hash']
	else:
		print('Fund is 0, no entries')
		winner = 'None'

	next_event = int(time.time() + draw_gap)
	#print(next_event)
	#print(last_block)
	db.insert({'next_event' : next_event, 'last_block' : last_block, 'winner' : winner, 'contestents' : addresses })
	#print(db.all())
	threading.Timer(draw_gap, lotto_loop).start()

@app.route('/lotto')
def start():
	f = open('store.pckl', 'rb')
	object = pickle.load(f)
	f.close()
	old_fund = int(object['funds'])
	#Check Balance
	r = requests.post('http://yapraiwallet.space:5000/get_balance', data = {'id_key': id_key, 'address' : fund_address})
	total_fund = int(r.json()['rai']) / 1000000

	result = db.all()
	total_num = len(result) - 1

	#To reduce calls to API, if the fund balance hasn't changed then don't need to check for addresses
	if old_fund != total_fund:
		old_fund = total_fund
		last_block = result[total_num]['last_block']

		r = requests.post('http://yapraiwallet.space:5000/get_history', data = {'id_key': id_key, 'address' : fund_address, 'count' : 50, 'filter' : last_block})
		addresses = []
		for contestents in r.json()['history']:
			if contestents['type'] == 'receive' and contestents['rai'] >= 1000000:
				addresses.append(contestents['account'])
	else:
		addresses = object['addresses']

	next_event = result[total_num]['next_event']
	winner = result[total_num]['winner']
	now = int(time.time())
	time_until_event = next_event - now
	print('%d = %d - %d' % (time_until_event, next_event, now))
	object = {'addresses' : addresses, 'funds' : old_fund}
	f = open('store.pckl', 'wb')
	pickle.dump(object, f)
	f.close()
	return render_template('start.html', total_fund=total_fund, time_until_event=time_until_event, draw_gap=int(draw_gap/60), winner=winner, addresses=addresses)


if __name__ == "__main__":
	lotto_loop()
	app.run(port=6000)
