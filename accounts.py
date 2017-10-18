import datetime
import json
import random
import salesforce
import time

def generate_new_account(name, code, entity, settlement_type, base_currency):
	account = {}
	account['ObjectType'] = 'Account'
	account['Action'] = 'Create'
	account['Entity'] = entity
	account['Name'] = name
	account['AccountCode'] = code
	account['CounterpartyType'] = 'Company'
	account['LegalName'] = name
	account['Status'] = 'Active'
	account['BaseCurrency'] = base_currency
	account['SettlementType'] = settlement_type

	return account

def push_accounts(names):
	input_list = []
	for name in names:
		base_currency = ['EUR', 'USD', 'CAD', 'GBP'][random.randint(0,3)]
		new_account = generate_new_account(name, name, 'MT4TEST', 'MT4 CLIENT', base_currency)
		input_list.append(new_account)

	o = salesforce.OrgConnection()

	request = json.dumps({"submit":input_list})
	print request
	o.conn.request('POST', '/services/apexrest/Kooltra/staticdata/Account', headers=o.headers, body=request)

	print o.conn.getresponse().reason



def main():
	for i in range(10):
		batch = 8
		names = ['EOD' + str(j) for j in range(i*batch, i*batch+batch)]
		push_accounts(names)
		time.sleep(2)

if __name__ == '__main__':
	main()




