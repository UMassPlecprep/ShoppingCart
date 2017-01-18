from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery
import datetime, os, httplib2
scopes = ['https://www.googleapis.com/auth/calendar']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/plecprepShoppingCart/keys.json',scopes=scopes)

http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar','v3',http=http)
now = datetime.datetime.utcnow().isoformat() + 'Z'
print 'Getting the upcoming 10 events'
eventsResult = service.events().list(
    calendarId='certl@umass.edu',timeMin=now,maxResults=10,singleEvents=True,
    orderBy='startTime').execute()
events = eventsResult.get('items',[])

if not events:
    print "No events"
for event in events:
    start = event['start'].get('dateTime',event['start'].get('date'))
    print start, event['summary']


