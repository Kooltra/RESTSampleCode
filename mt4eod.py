import datetime
import json
import random
import salesforce
import requests
import time

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


def main():
	o = salesforce.OrgConnection('Kooltra')
	num_batches = 1
	for i in range(num_batches):
		batch = 1
#accounts = ['EOD' + str(j) for j in range(i*batch, i*batch+batch)]
		accounts = ['MTT2']

		positions = get_positions(o, accounts)
		run_eod(o, positions)

if __name__ == '__main__':
	main()

