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

def inittemplate(env, template):
    #todo find a way to remove domain specific logic
    if template['Type'] == 'FxTrade__c':
        template['accounts'] = loadallids(env,'Account')


def generatefields(idx, template):
    ts = int(time.time() * 1000)
    fields = { k: v.format(
                index=str(idx),
                timestamp=ts
            ) for k, v in template['Fields'].items()
        }
    #todo find a way to remove domain specific logic
    if template['Type'] == 'Account':
        fields['BaseCurrency__c'] = ['EUR', 'USD', 'CAD', 'GBP'][random.randint(0,3)]
    elif template['Type'] == 'FxTrade__c':
        ccy_pairs = ['USDCAD', 'GBPUSD', 'EURUSD', 'USDCHF', 'GBPUSD', 'EURCAD', 'USDNZD', 'USDJPY', 'AUDUSD']
        pair = ccy_pairs[random.randint(0,len(ccy_pairs)-1)]
        fields['TradeDate__c'] = datetime.datetime.today()
        fields['Action__c'] = ['BUY', 'SELL'][random.randint(0,1)]
        fields['Account__c'] = template['accounts'][random.randint(0,len(template['accounts'])-1)]
        fields['Amount1__c'] = 1000*idx
        fields['Rate__c'] = 1.2+idx/100.0
        fields['Amount2__c'] = fields['Amount1__c']*fields['Rate__c']
        fields['Currency1__c'] = pair[:3]
        fields['Currency2__c'] = pair[3:]
    return fields


def main():

    if len(sys.argv) < 4:
        print('usage: python3 insert.py [env] [template file] [record count]')
        return -1

    env = sys.argv[1]
    templatefile = sys.argv[2]
    print('loading ' + templatefile)
    template = json.load(open(templatefile, 'r'))
    inittemplate(env,template)

    total = int(sys.argv[3])
    print('creating {total} {object}s'.format(total=str(total), object=template['Type']))
    accounts = [generatefields(idx, template) for idx in range(total)]

    print('connecting to salesforce bulk api with env {env}'.format(env=env))
    creds = json.load(open('env/{env}/credentials.json'.format(env=env), 'r'))
    bulk = SalesforceBulk(
        username=creds['username'],
        password=creds['password'],
        security_token=creds['token'])

    print('creating bulk job')
    job = bulk.create_insert_job(template['Type'], contentType='CSV')
    csv_iter = CsvDictsAdapter(iter(accounts))
    batch = bulk.post_batch(job, csv_iter)
    bulk.close_job(job)

    print('waiting for batch')
    t0 = time.time()
    while not bulk.is_batch_done(batch):
        print('.',end='')
        sys.stdout.flush()
        sleep(0.5)
    print('.')
    t1 = time.time()

    results = bulk.get_batch_results(batch)
    failures = 0
    successes = 0
    for result in results:
        if result.success:
            successes+=1
        else:
            failures+=1
        print(result)

    print("%d failure, %d success" % (failures, successes))
    print('saving history')
    saveids(env,template['Type'],[result.id for result in results])

    print("done in %.2fs" % (t1-t0))

if __name__ == '__main__':
	main()
