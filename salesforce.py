import json
import urllib
import httplib

org_base_url = "login.salesforce.com"
oauth_suffix = "/services/oauth2/token"

creds = json.load(open("credentials.json", 'r'))

class OrgConnection(name_space=''):
	conn = httplib.HTTPSConnection(org_base_url)
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	base_url = '/services/apexrest/'
	if name_space:
		base_url += name_space + '/'

	def __init__(self):
		self.conn.request('POST', oauth_suffix + '?' + urllib.urlencode(creds),
			headers=self.headers)
		res = self.conn.getresponse()
		res_json = json.load(res)

		self.headers["Content-Type"] = "application/json"
		self.headers["Authorization"] = 'Bearer ' + res_json.get('access_token')
		instance_url = res_json.get('instance_url')
		self.conn = httplib.HTTPSConnection(instance_url[8:])


o = OrgConnection()
