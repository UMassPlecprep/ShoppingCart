from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery
import httplib2

scopes = ['https://www.googleapis.com/auth/calendar']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/plecprepShoppingCart/keys.json',scopes=scopes)
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar','v3',http=http)
