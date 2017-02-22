from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery, errors
from oauth2client.file import Storage
import httplib2, base64, os, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email():
    to_email = 'plecprep@umass.edu'
    from_email = 'plecprepserver@gmail.com'

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        cred_dir = os.path.join(home_dir, '.credentials')
        cred_path = os.path.join(cred_dir, 'gmail-python-quickstart.json')
        store = Storage(cred_path)
        creds = store.get()
        return creds

    def SendMessage(self,message):
        http = self.get_credentials().authorize(httplib2.Http())
        service = discovery.build('gmail','v1', http=http)
        try:
            message = (service.users().messages().send(userId=self.from_email, body=message).execute())
            print 'Message Id: {}'.format(message['id'])
            return message
        except errors.HttpError, error:
            print 'An error occurred: %s' % error

    def create_attachment_message(self, file_string='test.csv'):
        message = MIMEMultipart()
        message['to'] = self.to_email
        message['from'] = self.from_email
        message['subject'] = "Semesterly demo requests spreadsheet"
        msg = MIMEText("Your semesterly demos report")
        message.attach(msg)
        
        print file_string
        with open(file_string,'rb') as fp:
            msg = MIMEText(fp.read(), _subtype=sub_type)
        filename = os.path.basename(file_string)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def CreateMessage(self, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = self.to_email
        message['from'] = self.from_email
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}
