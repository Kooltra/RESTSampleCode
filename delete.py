from salesforce_bulk import CsvDictsAdapter
from salesforce_bulk import SalesforceBulk
from time import sleep
from history import loadallids
from history import clearhistory
import sys
import json
import time

def main():

    if len(sys.argv) < 3:
        print('usage: python3 delete.py [env] [object type]')
        return -1
    env = sys.argv[1]
    objecttype = sys.argv[2]

    print('connecting to salesforce bulk api with env {env}'.format(env=env))
    creds = json.load(open('env/{env}/credentials.json'.format(env=env), 'r'))
    bulk = SalesforceBulk(
        username=creds['username'],
        password=creds['password'],
        security_token=creds['token'])

    print('creating bulk job')
    job = bulk.create_delete_job(objecttype, contentType='CSV')
    accounts = [dict(Id=idx) for idx in loadallids(env,objecttype)]
    csv_iter = CsvDictsAdapter(iter(accounts))
    batch = bulk.post_batch(job, csv_iter)
    #bulk.wait_for_batch(job, batch)
    bulk.close_job(job)


    print('waiting for batch')
    t0 = time.time()
    while not bulk.is_batch_done(batch):
        print('.',end='')
        sys.stdout.flush()
        sleep(0.5)
    t1 = time.time()

    for result in bulk.get_batch_results(batch):
        print(result)

    print('clearing history')
    clearhistory(env,objecttype)
    if objecttype.lower() == 'account':
        clearhistory(env, 'FxTrade__c')

    print("done in %.2fs" % (t1-t0))


if __name__ == '__main__':
	main()
