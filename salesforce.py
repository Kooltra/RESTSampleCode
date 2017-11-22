import json
import urllib.parse
import requests
import http.client

org_base_url = "https://login.salesforce.com"
oauth_suffix = "/services/oauth2/token"

creds = json.load(open("credentials.json", 'r'))

class OrgConnection:
	headers = {"Content-Type": "application/x-www-form-urlencoded"}

	def __init__(self, name_space=''):
		res = requests.post(org_base_url + oauth_suffix + '?' + urllib.parse.urlencode(creds),
			headers=self.headers)

		res_json = json.loads(res.text)
		self.headers["Content-Type"] = "application/json"
		self.headers["Authorization"] = 'Bearer ' + res_json.get('access_token')
		self.base_url = res_json.get('instance_url') + '/services/apexrest/'
		if name_space:
			self.base_url += name_space + '/'

