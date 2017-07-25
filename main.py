import json
import urllib
import httplib

org_base_url = "login.salesforce.com"
oauth_suffix = "/services/oauth2/token"

creds = json.load(open("credentials.json", 'r'))

class OrgConnection():
	conn = httplib.HTTPSConnection(org_base_url)
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	instance_url = ''

	def __init__(self):
		self.conn.request('POST', oauth_suffix + '?' + urllib.urlencode(creds),
			headers=self.headers)
		res = self.conn.getresponse()
		self.headers["Authoriztion"] = 'Bearer ' + json.load(res).get('access_token')
		self.instance_url = json.load(res).get('instance_url')


o = OrgConnection()
