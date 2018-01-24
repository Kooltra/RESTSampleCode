import datetime
import json
import random
import requests
import time
import sys
import unicodecsv
from history import loadallids
from dump import getaccountcodes
from salesforce_bulk import CsvDictsAdapter
from salesforce_bulk import SalesforceBulk
from simple_salesforce import Salesforce
from functools import partial

namespaceAPI = ''
namespacePrefix = ''
if len(sys.argv) > 3:
	namespaceAPI = sys.argv[3] + '/'
	namespacePrefix = sys.argv[3] + '__'

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	CLEARLINE = '\r\033[K'

class DataLoader:
	def __init__(self,env,entity):
		creds = json.load(open('env/{env}/credentials.json'.format(env=env), 'r'))
		self.bulk = SalesforceBulk(
	        username=creds['username'],
	        password=creds['password'],
	        security_token=creds['token'])
		self.entity = entity
		self.rest = Salesforce(
	        username=creds['username'],
	        password=creds['password'],
	        security_token=creds['token'])

	def wait(self, batch):
		while not self.bulk.is_batch_done(batch):
			print('.',end='')
			sys.stdout.flush()
			time.sleep(0.5)
		print('')

	def clean(self, type):
		job = self.bulk.create_query_job(type, contentType='CSV')
		print('cleaning '+type)
		batch = self.bulk.query(job, ('SELECT Id FROM {type} WHERE '+namespacePrefix+'Entity__c=\'{entity}\'').format(type=type, entity=self.entity))
		self.bulk.close_job(job)
		self.wait(batch)

		#get ids
		ids = []
		for result in self.bulk.get_all_results_for_query_batch(batch):
		    reader = unicodecsv.DictReader(result, encoding='utf-8')
		    for row in reader:
		        ids.append(row['Id'])

		#delete ids
		if len(ids) > 0:
			self.delete(type, ids)

	def delete(self, type, ids):
		job = self.bulk.create_delete_job(type, contentType='CSV')
		dictids = [dict(Id=idx) for idx in ids]
		csv_iter = CsvDictsAdapter(iter(dictids))
		batch = self.bulk.post_batch(job, csv_iter)
		self.bulk.close_job(job)
		self.wait(batch)
		print('done')


	def update(self, type, values):
		job = self.bulk.create_update_job(type, contentType='CSV')
		csv_iter = CsvDictsAdapter(iter(values))
		batch = self.bulk.post_batch(job, csv_iter)
		self.bulk.close_job(job)
		self.wait(batch)
		print('done')


	def query(self, query):
		return self.rest.query(query)


def queryuntil(dl, query, until, maxretry = 3):
	shouldcontinue = False
	retries = 0
	while shouldcontinue == False:
		res = dl.query(query)
		shouldcontinue = until(res)
		if shouldcontinue == False:
			retries += 1
			if retries >= maxretry:
				print((bcolors.FAIL+bcolors.CLEARLINE+'\t\t✘ failed (%d retries)'+bcolors.ENDC) % retries)
				shouldcontinue = True
			else:
				print(bcolors.CLEARLINE+'\t\tchecking... (%d retries)' % retries,end='')
			sys.stdout.flush()
			time.sleep(1)
		else:
			print(bcolors.OKGREEN+bcolors.CLEARLINE+'\t\t✔ passed'+bcolors.ENDC)

def today():
	return datetime.datetime.today().strftime('%Y-%m-%d')

def yesterday():
	return (datetime.timedelta(days=-1) + datetime.datetime.today()).strftime('%Y-%m-%d')

def validateSnapshotsCreated(dl):
	query = ('SELECT Id FROM '+ \
		namespacePrefix+'Snapshot__c WHERE '+ \
		namespacePrefix+'Entity__c=\'{entity}\' AND '+ \
		namespacePrefix+'Date__c={date}').format(
		entity=dl.entity, date=today())
	queryuntil(dl, query, lambda res: res['totalSize'] > 0)

def validateCurrencyPairTenors(dl):
	query = ('SELECT Id FROM ' + \
		namespacePrefix+'CurrencyPair__c WHERE ('+ \
		namespacePrefix+'IsStandard__c=true OR '+ \
		namespacePrefix+'isBasebase__c=true) AND Name=\'USDCAD\' AND '+ \
		namespacePrefix+'valueDateON__c>{date}').format( \
		date=yesterday())
	queryuntil(dl, query, lambda res: res['totalSize'] > 0)

def validateSnapshotsPopulated(dl):
	query = ('SELECT Id, '+ \
		namespacePrefix+'RawUSDEquity__c FROM '+ \
		namespacePrefix+'Snapshot__c WHERE '+ \
		namespacePrefix+'Entity__c=\'{entity}\' AND '+ \
		namespacePrefix+'Date__c={date} AND '+ \
		namespacePrefix+'RawUSDEquity__c <> NULL').format( \
		entity=dl.entity, date=today())
	queryuntil(dl, query, lambda res: res['totalSize'] > 0, 60)

def validateNOPs(dl):
	query = ('SELECT Id, '+ \
		namespacePrefix+'FxNOP__c FROM Account WHERE '+ \
		namespacePrefix+'Entity__c=\'{entity}\'').format( \
		entity=dl.entity)
	queryuntil(dl, query, lambda res: all(record[namespacePrefix+'FxNOP__c'] != None for record in res['records']) > 0, 60)

def validateSnapshotsPositionsCsv(dl):
	query = ('SELECT (select Id, Name from Attachments where name=\'Positions.csv\') FROM '+ \
		namespacePrefix+'Snapshot__c WHERE '+ \
		namespacePrefix+'Entity__c=\'{entity}\' AND '+ \
		namespacePrefix+'Date__c={date}').format( \
		entity=dl.entity, date=today())
	queryuntil(dl, query, lambda res: (res['totalSize'] > 0 and res['records'][0]['Attachments'] != None), 60)

def describe(description):
	print(description)

def it(description, f, dl):
	print('\t'+description)
	f(dl)


def main():

	if len(sys.argv) < 3:
		print('usage: python3 eod.py [env] [entity] [namespace]')
		return -1

	env = sys.argv[1]
	entityIdsString = sys.argv[2]
	entityIds = entityIdsString.split(',')

	dataLoaders = [DataLoader(env, entityId) for entityId in entityIds]

	for dl in dataLoaders:
		dl.clean(namespacePrefix+'Snapshot__c')

	#reset valueDate on USDCAD for test
	# getattr(dl.rest,namespacePrefix+'CurrencyPair__c').update(
	# 	dl.query('Select Id from '+namespacePrefix+'CurrencyPair__c WHERE Name=\'USDCAD\'')['records'][0]['Id'],
	# 		{namespacePrefix+'valueDateON__c': yesterday()})

	#reset FxNOP__c for accounts
	# accounts = [{'Id':idx, namespacePrefix+'FxNOP__c': 0} for idx in loadallids(env,'Account')]
	# dl.update('Account',accounts)

	#set value date to today for trades
	# trades = [{'Id':idx, namespacePrefix+'ValueDate__c':datetime.datetime.today()} for idx in loadallids(env,namespacePrefix+'FxTrade__c')]
	# dl.update(namespacePrefix+'FxTrade__c',trades)

	# execute EOD
	print(dl.rest.apexecute(namespaceAPI+'EOD', method='POST', data={'method': 'devEOD','entityId': entityIdsString}))
	return;

	# describe('preEOD')
	it('updates currency pair tenors', validateCurrencyPairTenors, dl)
	it('creates snapshots', validateSnapshotsCreated, dl)


	describe('postProcess')
	it('populates snapshots', validateSnapshotsPopulated, dl)
	# print(dl.rest.apexecute(namespaceAPI+'EOD', method='POST', data={'method': 'postProcess','entityId': entity}))
	it('creates positions.csv', validateSnapshotsPositionsCsv, dl)


	describe('update NOPs')
	# print(dl.rest.apexecute('EOD', method='POST', data={'method': 'UpdateAccountNOPs','entityId': entity}))
	it('account NOPs calculated', validateNOPs, dl)


if __name__ == '__main__':
	main()
