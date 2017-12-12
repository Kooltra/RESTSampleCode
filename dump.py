from salesforce_bulk import CsvDictsAdapter
from salesforce_bulk import SalesforceBulk
from time import sleep
from history import loadallids
from history import saveids
import sys
import json
import time
import datetime
import random
import unicodecsv

def getaccountcodes(env, entityid):
    creds = json.load(open('env/{env}/credentials.json'.format(env=env), 'r'))
    bulk = SalesforceBulk(
        username=creds['username'],
        password=creds['password'],
        security_token=creds['token'])
    job = bulk.create_query_job('Account', contentType='CSV')
    batch = bulk.query(job,
        'SELECT Code__c FROM Account WHERE Entity__c=\'{entity}\''
        .format(entity=entityid))
    bulk.wait_for_batch(job, batch)
    bulk.close_job(job)
    codes = []
    for result in bulk.get_all_results_for_query_batch(batch):
        reader = unicodecsv.DictReader(result, encoding='utf-8')
        for row in reader:
            codes.append(row['Code__c'])
    return codes

def main():

    if len(sys.argv) < 4:
        print('usage: python3 dump.py [env] [object type] [entity id]')
        return -1

    env = sys.argv[1]
    objecttype = sys.argv[2]
    entityid = sys.argv[3]

    print('connecting to salesforce bulk api with env {env}'.format(env=env))
    creds = json.load(open('env/{env}/credentials.json'.format(env=env), 'r'))
    bulk = SalesforceBulk(
        username=creds['username'],
        password=creds['password'],
        security_token=creds['token'])

    print('creating bulk job')
    job = bulk.create_query_job(objecttype, contentType='CSV')
    batch = bulk.query(job,
        'SELECT Id FROM {type} WHERE Entity__c=\'{entity}\''
        .format(type=objecttype, entity=entityid))
    bulk.close_job(job)

    print('waiting for batch')
    t0 = time.time()
    while not bulk.is_batch_done(batch):
        print('.',end='')
        sys.stdout.flush()
        sleep(0.5)
    t1 = time.time()


    ids = []
    for result in bulk.get_all_results_for_query_batch(batch):
        reader = unicodecsv.DictReader(result, encoding='utf-8')
        for row in reader:
            ids.append(row['Id'])

    print('saving history')
    saveids(env,objecttype,[result.id for result in results])
    #print('saving history')
    #saveids(env,template['Type'],[result.id for result in results])

    print("done in %.2fs" % (t1-t0))

if __name__ == '__main__':
	main()
