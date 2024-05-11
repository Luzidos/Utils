from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient import errors
from email.mime.text import MIMEText
from email.message import EmailMessage
from email import message_from_bytes
import os.path
import base64
from io import BytesIO
from bs4 import BeautifulSoup
import re
import sys
import os
import requests
from luzidos_utils.aws_io.s3 import read as s3_read
from luzidos_utils.aws_io.s3 import write as s3_write
from luzidos_utils.aws_io.s3 import file_paths as s3_fp
from luzidos_utils.openai.gpt_call import get_gpt_response
from luzidos_utils.email import prompts
import uuid
import json

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

class GmailClient:
    def __init__(self, credentials_file, scopes, user_id):
        self.service = None
        self.creds = self.get_service_account_credentials(user_id, credentials_file, scopes)
        self.user_id = user_id
        if self.creds:
            self.service = build("gmail", "v1", credentials=self.creds)

    # Fetch messages based on the query - read/unread
    def upload_unread_messages_to_s3(self, query):
        """Get messages from the user's mailbox.
        Uploads all of the unread messages to s3 in the format that I chose
        It also uploads all of its relevant attachments to s3
        It also applies ocr to the attachments and uploads the ocr data to s3
        Args:
            query: The query string used to filter messages.
        Returns:
            A dictionary of messages.
        """
        if len(query) == 0:
            try:
                threads = (self.service.users().threads().list(userId="me").execute().get("threads", []))
            except errors.HttpError as error:
                print(f'An error occurred: {error}')

        else:
            threads = (self.service.users().threads().list(userId="me", q=query).execute().get("threads", []))

        

        thread_ids = []
        for thread in threads:
            tdata = (self.service.users().threads().get(userId="me", id=thread["id"]).execute())
            nmsgs = len(tdata["messages"])
            print("Messages per thread: ", nmsgs)

            threadObj = {}
            threadObj['thread_id'] = thread['id']
            threadObj['messages'] = {}
            email_data = s3_read.read_email_body_from_s3(self.user_id, thread["id"])

            for rawMsgObj in tdata["messages"]:       
                if email_data and rawMsgObj['id'] in email_data["messages"]:
                    threadObj['messages'][rawMsgObj['id']] = email_data["messages"][rawMsgObj['id']]
                    continue
                extracted_data = {}
                keys_of_interest = ['From', 'To', 'Date', 'Subject']

                for header in rawMsgObj['payload']['headers']:
                    if header['name'] in keys_of_interest:
                        extracted_data[header['name']] = header['value']

                extracted_data['labelIds'] = rawMsgObj['labelIds']
                message_contents = self.__parse_message(rawMsgObj)
                extracted_data['body'] = message_contents["body"]
                extracted_data['attachments'] = message_contents["attachments"]

                msgObj = extracted_data
                msgObj['message_id'] = rawMsgObj['id']
                threadObj['messages'][rawMsgObj['id']] = msgObj 

                if "UNREAD" in rawMsgObj['labelIds']:
                    print(f"Marking message {rawMsgObj['id']} as read.")
                    self.__mark_message_as_read(rawMsgObj['id'])
                else:
                    print(rawMsgObj['labelIds'])
            thread_ids.append(threadObj['thread_id'])
            s3_write.upload_email_body_to_s3(self.user_id, threadObj['thread_id'], threadObj)
        return thread_ids
    
    def send_message(self, sender, to, subject, body, attachments=None, cc=None, thread_id=None, message_id=None):
        """Create and send an email message
        Print the returned  message id
        Returns: Message object, including message id

        """
    
        try:
            message = EmailMessage()
            message.set_content(body)

            message["To"] = to
            message["From"] = sender
            message["Subject"] = subject

            if cc:
                message["Cc"] = cc

            if message_id:
                message["In-Reply-To"] = message_id
                message["References"] = message_id

            if attachments:
                for file_path in attachments:
                    bucket_name = file_path.split('/')[0]
                    file_name = file_path.split('/')[-1]
                    object_name = '/'.join(file_path.split('/')[1:])
                    file_data = s3_read.read_file_from_s3(bucket_name, object_name)
                    message.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            if thread_id:
                create_message["threadId"] = thread_id
            send_message = (
                self.service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None
        return send_message
    
    def reply_to_message(self, thread_id, body, attachments=None, reply_all=False):
        """Reply to an existing email thread."""
        try:
            # Fetch the last message from the thread
            thread = self.service.users().threads().get(userId="me", id=thread_id, format="metadata").execute()
            messages = thread['messages']
            last_message = messages[-1]
            # Prepare reply headers
            headers = {header['name']: header['value'] for header in last_message['payload']['headers']}
            last_message_id = headers.get('Message-Id')
            subject = headers.get('Subject')

            to = headers.get('From')  # Reply to sender
            if reply_all:
                cc = headers.get('To', '') + ', ' + headers.get('Cc', '')
            else:
                cc = None

            # Prepare and send the reply
            return self.send_message(
                sender="me", 
                to=to, 
                subject=subject, 
                body=body, 
                attachments=attachments, 
                cc=cc,
                thread_id=thread_id,
                message_id=last_message_id
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def __mark_message_as_read(self, message_id):
        """Marks a message as read by removing the 'UNREAD' label."""
        try:
            body = {'removeLabelIds': ['UNREAD']}
            self.service.users().messages().modify(userId="me", id=message_id, body=body).execute()
        except errors.HttpError as error:
            print(f'An error occurred: {error}')


    def __handle_attachments(self, payload, tdata):
        """Download all attachments from a given email."""
        attachment_ids = []
        for part in payload['parts']:
            if part['filename']:
                bucket_name = s3_fp.ROOT_BUCKET

                attachment_id = part['body']['attachmentId']
                attachment = self.service.users().messages().attachments().get(userId="me", messageId=tdata, id=attachment_id).execute()
                data = attachment['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                # Use BytesIO for in-memory file
                file_obj = BytesIO(file_data)

                attachment_filename = part['filename']
                email_id = tdata['threadId']

                attachment_type = attachment_filename.split('.')[-1]
                attachment_name = ".".join(attachment_filename.split('.')[:-1])
                # create using UUID
                attachment_id = str(uuid.uuid4())
                # Upload to S3
                if s3_write.upload_email_attachment_to_s3(self.user_id,email_id, file_obj, f"{attachment_id}.{attachment_type}"):
                    print(f"Attachment {part['filename']} uploaded to S3.")
                else:
                    print(f"Failed to upload {part['filename']}.")

                attachment_data = {}
                attachment_data["attachment_id"] = attachment_id
                attachment_data["attachment_name"] = attachment_name
                attachment_data["attachment_type"] = attachment_type
                # Apply OCR
                ocr_api_url = "https://62n2j8msb4.execute-api.us-west-2.amazonaws.com/ocr_testing/ocr"
                params = {'s3_bucket': bucket_name, 's3_key': s3_fp.EMAIL_ATTACHMENT_PATH(self.user_id, email_id, f"{attachment_id}.{attachment_type}")}
                ocr_response = requests.get(ocr_api_url, params=params)
                if ocr_response.status_code == 200:
                    ocr_data = ocr_response.json()
                    attachment_data["attachment_OCR"] = ocr_data.get("text", "OCR failed or returned no text.")
                else:
                    attachment_data["attachment_OCR"] = ocr_data.get("text", "OCR failed or returned no text.")

                # Summarize email
                summarize_prompt = prompts.SUMMARIZE_ATTAACHMENT_PROMPT(attachment_type, attachment_name, attachment_data["attachment_OCR"])
                attachment_data["attachment_description"] = get_gpt_response(summarize_prompt)
                # upload data
                s3_write.upload_email_attachment_json_to_s3(self.user_id, email_id, f"{attachment_id}.json", attachment_data)
                attachment_ids.append(attachment_id)

        return attachment_ids


    def __parse_message(self, tdata):
        """Parse a single message to extract details including full content."""
        payload = tdata["payload"]

        hasFile = False
        if 'parts' in payload:
            for part in payload['parts']:
                if part['filename']:
                    hasFile = True
                    
        message_body = self.__decode_email_payload(payload)
        attachment_ids = []
        if hasFile:
            attachment_ids = self.__handle_attachments(payload, tdata)
        return {"body": message_body, "attachments": attachment_ids}

    


    def __decode_email_payload(self, payload):
        """
        Decodes email payload from base64url encoding.
        
        :param payload: The payload of the email obtained from the Gmail API.
        :return: The decoded email content.
        """
        # Determine the message format (plain text, HTML, or multipart)
        mime_type = payload['mimeType']
        parts = payload.get('parts', [])
        
        if mime_type == 'text/plain' or mime_type == 'text/html':
            # Simple email with text or HTML content
            data = payload['body']['data']
            decoded_data = base64.urlsafe_b64decode(data.encode('ASCII'))
            return decoded_data.decode('utf-8')
        elif mime_type.startswith('multipart/'):
            # Multipart email (e.g., text and HTML, attachments, etc.)
            for part in parts:
                # Recursively decode each part
                part_body = self.__decode_email_payload(part)
                if part_body:
                    return part_body
        return None



    def get_service_account_credentials(self, user_id, credentials_file, scopes):
        """
        Retrieve Gmail API credentials using a service account.
        :param credentials_file: Path to the service account JSON file.
        :param scopes: Scopes needed for the Gmail API.
        :return: Credentials object.
        """
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        return creds

def get_gmail_client(user_id):
    scopes = ['https://www.googleapis.com/auth/gmail.modify']

    credentials_file = s3_read.read_credentials_file_from_s3(user_id)
    gmail_client = GmailClient(credentials_file, scopes, user_id)
    return gmail_client

# Usage
#scopes = ['https://www.googleapis.com/auth/gmail.modify']
#gmail_client = GmailClient('token.json', 'credentials.json', scopes)

#messageObj = gmail_client.get_messages('is:unread') # is:unread or is:read
#print(messageObj) # Object with all threads and their messages and the attachments
