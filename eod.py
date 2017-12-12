import datetime
import json
import random
import salesforce
import requests
import time
from history import loadallids
from dump import getaccountcodes

def main():
	o = salesforce.OrgConnection('')
	res = requests.post(o.base_url + 'EOD', headers=o.headers)
	print(res.text)

if __name__ == '__main__':
	main()
