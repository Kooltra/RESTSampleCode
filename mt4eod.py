import datetime
import json
import random
import salesforce
import requests
import time
import math
from history import loadallids
from dump import getaccountcodes

def get_positions(o, account_codes):

	input_list = []

	for ac in account_codes:
		input_list.append({'AccountCode': ac})

	request = json.dumps({"submit":input_list})

	res = requests.post(o.base_url + 'retrieve/AccountsPositions', headers=o.headers, data=request)
	res = json.loads(res.text)
	return  res[0].get('accPositions')


def run_eod(o, positions):
	mt4_request = {}
	for p in positions:
		send_eod_request(o, p)
		time.sleep(0.5)


def send_eod_request(o, position):
	pairs = []
	mt4_request = {
		'accountCode': position.get('code'),
		'rolls': 20,
		'balance': 4000,
		'commissions': -77,
		'ExecutionCutoffTime': int(round(time.time() * 1000))
	}

	ins_positions = position.get('insPositions')
	for p in ins_positions:
		pairs.append({'rate': 1.66, 'name': p.get('pairName'), 'amount': 0 - float(p.get('positionAmount'))})

	mt4_request['CCYPairs'] = pairs

	request = json.dumps({'submit':[mt4_request]})
	res = requests.post(o.base_url + 'MT4BalanceMatching', headers=o.headers, data=request)
	print(res.text)

def main():
	o = salesforce.OrgConnection('')
	accounts = getaccountcodes('core','a0A1C00000jaIFj')
	batch_size = 10
	num_batches = math.ceil(len(accounts)/batch_size)

	for i in range(num_batches):
		positions = get_positions(o, accounts[(i * batch_size):((i+1) * batch_size)])
		run_eod(o, positions)

if __name__ == '__main__':
	main()
