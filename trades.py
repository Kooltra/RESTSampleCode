import datetime
import json
import random
import salesforce
import time
import requests

def generate_new_spot_trade(account_code, trade_action, notional, rate, ccy1, ccy2, isMargin):
	trade = {
		'ObjectType': 'Trade',
		'Action': 'Create',
		'Status': 'Open',
		'Type': 'FXSPOT',
		'TradeDate': str(datetime.datetime.today())[:10].replace('-',''),
		'TradeAction': trade_action,
		'ExecutionTime': int(round(time.time() * 1000)),
		'AccountCode': account_code,
		'Notional': notional,
		'Rate': rate,
		'CCY1': ccy1,
		'CCY2': ccy2,
		'CounterAmount': notional * rate
	}

	if not isMargin:
		trade['ValueDate'] = '20171122'#str(datetime.datetime.today())[:10].replace('-','')

	return trade

def push_trades(o, account_code, num):
	input_list = []
	for i in range(num):
		buysell = ['BUY', 'SELL'][random.randint(0,1)]
		ccy_pairs = ['USDCAD', 'GBPUSD', 'EURUSD', 'USDCHF', 'GBPUSD', 'EURCAD', 'USDNZD', 'USDJPY', 'AUDUSD']
		#ccy_pairs = ccy_pairs + ['EURAUD', 'EURJPY', 'EURCHF', 'EURGBP', 'AUDCAD', 'GBPCHF', 'GBPJPY']
		#ccy_pairs = ccy_pairs + ['CHFJPY', 'AUDJPY', 'AUDNZD']
		pair = ccy_pairs[random.randint(0,len(ccy_pairs)-1)]
		new_trade = generate_new_spot_trade(account_code, buysell, 1000+i, 1.2+i/100.0, pair[:3], pair[3:], True)
		input_list.append(new_trade)

	request = json.dumps({"submit":input_list})

	res = requests.post(o.base_url + 'transactions/Trade', headers=o.headers, data=request)
	print(res.text)


def main():
	o = salesforce.OrgConnection('Kooltra')

	num_accounts = 1
	for account in range(num_accounts):
		accountCode = 'MTT2' #'EOD' + str(account) #accountCode = 'EOD0'
		num_trade_batches = 4
		batch_size = 3
		for i in range(num_trade_batches):
			push_trades(o, accountCode, batch_size)
			time.sleep(1)

if __name__ == '__main__':
	main()




