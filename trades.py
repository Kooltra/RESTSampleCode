import datetime
import json
import random
import salesforce
import time
import calendar

def generate_new_spot_trade(account_code, trade_action, notional, rate, ccy1, ccy2, isMargin):
	trade = {}
	trade['ObjectType'] = 'Trade'
	trade['Action'] = 'Create'
	trade['Status'] = 'Open'
	trade['Type'] = 'FXSPOT'
	trade['TradeDate'] = str(datetime.datetime.today())[:10].replace('-','')
	trade['TradeAction'] = trade_action
	trade['AccountCode'] = account_code
	trade['Notional'] = notional
	trade['Rate'] = rate
	trade['CCY1'] = ccy1
	trade['CCY2'] = ccy2
	trade['ExecutionTime'] = calendar.timegm(time.gmtime())*1000
	trade['CounterAmount'] = notional * rate

	if not isMargin:
		trade['ValueDate'] = str(datetime.datetime.today())[:10].replace('-','')

	return trade

def push_trades(account_code, num):
	input_list = []
	for i in range(num):
		buysell = ['BUY', 'SELL'][random.randint(0,1)]
		ccy_pairs = ['USDCAD', 'EURUSD', 'USDCHF', 'GBPUSD', 'EURCAD', 'USDNZD', 'USDJPY', 'AUDUSD']
		#ccy_pairs = ccy_pairs + ['EURAUD', 'EURJPY', 'EURCHF', 'EURGBP', 'AUDCAD', 'GBPCHF', 'GBPJPY']
		#ccy_pairs = ccy_pairs + ['CHFJPY', 'AUDJPY', 'AUDNZD']
		pair = ccy_pairs[random.randint(0,len(ccy_pairs)-1)]
		new_trade = generate_new_spot_trade(account_code, buysell, 1000+i, 1.2+i/100.0, pair[:3], pair[3:], True)
		input_list.append(new_trade)

	o = salesforce.OrgConnection()

	request = json.dumps({"submit":input_list})

	o.conn.request('POST', o.base_url + 'transactions/Trade', headers=o.headers, body=request)
	

num_accounts = 10
for account in range(num_accounts):
	accountCode = 'EOD' + str(account) #accountCode = 'EOD0'
	num_trade_batches = 20
	batch_size = 20
	for i in range(num_trade_batches):
		push_trades(accountCode, batch_size)
		#time.sleep(1)





