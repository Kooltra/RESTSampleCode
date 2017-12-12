import json
import urllib.parse
import requests

oauth_url = "https://login.salesforce.com/services/oauth2/token"

creds = json.load(open("credentials.json.core", 'r'))

class OrgConnection:
	headers = {"Content-Type": "application/x-www-form-urlencoded"}

	def __init__(self, name_space=''):
		res = requests.post(oauth_url + '?' + urllib.parse.urlencode(creds),
			headers=self.headers)
		res_json = json.loads(res.text)
		self.headers["Content-Type"] = "application/json"
		self.headers["Authorization"] = 'Bearer ' + res_json.get('access_token')
		self.base_url = res_json.get('instance_url') + '/services/apexrest/'
		self.query_url = res_json.get('instance_url') + '/services/data/v41.0/query/'
		if name_space:
			self.base_url += name_space + '/'

	def soql(self, query):
		res = requests.get(self.query_url + '?q=' + urllib.parse.quote_plus(query), headers=self.headers)
		res.raise_for_status()
		return res.text

o = OrgConnection()
