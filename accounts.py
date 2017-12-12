import datetime
import json
import random
import salesforce
import time
import requests

def generate_new_account(name, code, entity, settlement_type, base_currency):
	account = {
		'ObjectType': 'Account',
		'Action': 'Create',
		'Entity': entity,
		'Name': name,
		'AccountCode': code,
		'CounterpartyType': 'Company',
		'LegalName': name,
		'Status': 'Active',
		'BaseCurrency':  base_currency,
		'SettlementType': settlement_type
	}

	return account

def push_accounts(o, names, entity):
	input_list = []
	for name in names:
		base_currency = ['EUR', 'USD', 'CAD', 'GBP'][random.randint(0,3)]
		new_account = generate_new_account(name, name, entity, 'MT4 CLIENT', base_currency)
		input_list.append(new_account)

	request = json.dumps({"submit":input_list})
	res = requests.post(o.base_url + 'staticdata/Account', headers=o.headers, data=request)
	res.raise_for_status()
	print(res.text)

def main():
	num_batches = 1
	entity = 'RyanEODTest'
	o = salesforce.OrgConnection('')
	for i in range(num_batches):
		batch = 1
		names = ['RyanEOD' + str(j) for j in range(i*batch, i*batch + batch)]
		push_accounts(o, names, entity)
		time.sleep(2)

if __name__ == '__main__':
	main()
