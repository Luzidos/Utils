from utils.io.email.emailAPI import GmailClient
#
# Usage
scopes = ['https://www.googleapis.com/auth/gmail.modify']
gmail_client = GmailClient('token.json', '/Users/andrescarranza/Documents/GitHub/Luzidos/src/services/invoice_agent/utils/io/email/credentials.json', scopes, 'emailtester')

threads = gmail_client.upload_unread_messages_to_s3('is:unread') # is:unread or is:read