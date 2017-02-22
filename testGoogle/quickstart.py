import httplib2, os

from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print 'Storing credentials to ', credential_path
    return credentials

def main():
    creds = get_credentials()
    http = creds.authorize(httplib2.Http())
    service = discovery.build('gmail','v1', http=http)
    results = service.users().labels().list(userId='plecprep@umass.edu').execute()
    labels = results.get('labels',[])
    if not labels:
        print 'No labels found'
    else:
        print 'Labels: '
        for label in labels:
            print label['name']

if __name__ == '__main__':
    main()
