import datetime
import json
import random
import salesforce
import time

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
	trade['CounterAmount'] = notional * rate

	if not isMargin:
		trade['ValueDate'] = str(datetime.datetime.today())[:10].replace('-','')

	return trade

def push_trades(account_code, num):
	input_list = []
	for i in range(num):
		buysell = ['BUY', 'SELL'][random.randint(0,1)]
		ccy = ['EURGBP', 'EURUSD', 'USDCAD', 'AUDCAD', 'AUDUSD', 'GBPUSD', 'USDJPY'][random.randint(0,6)]
		new_trade = generate_new_spot_trade(account_code, buysell, 1000+i, 1.2+i/100.0, ccy[:3], ccy[3:], True)
		input_list.append(new_trade)

	o = salesforce.OrgConnection()

	request = json.dumps({"submit":input_list})

	o.conn.request('POST', '/services/apexrest/Kooltra/transactions/Trade', headers=o.headers, body=request)


for i in range(80):
	push_trades('MT4EODTEST', 15)
	time.sleep(2)





