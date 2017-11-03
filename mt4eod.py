import datetime
import json
import random
import salesforce
import time

def get_positions(account_codes, o):

	input_list = []

	for ac in account_codes:
		input_list.append({'AccountCode': ac})

	request = json.dumps({"submit":input_list})

	o.conn.request('POST', o.base_url + 'retrieve/AccountsPositions', headers=o.headers, body=request)
	return  json.load(o.conn.getresponse())[0].get('accPositions')


def run_eod(positions, o):
	mt4_request = {}
	for p in positions:
		send_eod_request(p, o)
		time.sleep(6)


def send_eod_request(position, o):
	pairs = []
	mt4_request = {}
	ins_positions = position.get('insPositions')
	for p in ins_positions:
		pairs.append({'rate': 1.66, 'name': p.get('pairName'), 'amount': 0 - float(p.get('positionAmount'))})

	mt4_request['accountCode'] = position.get('code')
	mt4_request['rolls'] = 20
	mt4_request['balance'] = 3000
	mt4_request['commissions'] = -77
	mt4_request['CCYPairs'] = pairs

	request = json.dumps({'submit':[mt4_request]})
	o.conn.request('POST', o.base_url + 'MT4BalanceMatching', headers=o.headers, body=request)

	print o.conn.getresponse().read()

def main():
	o = salesforce.OrgConnection()
	num_batches = 10
	for i in range(num_batches):
		batch = 1
		accounts = ['EOD' + str(j) for j in range(i*batch, i*batch+batch)]
		#accounts = ['EOD0']

		positions = get_positions(accounts, o)
		run_eod(positions, o)

if __name__ == '__main__':
	main()

