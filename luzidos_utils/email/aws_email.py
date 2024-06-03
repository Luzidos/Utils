from luzidos_utils.aws_io.s3 import read as s3_read
from luzidos_utils.aws_io.s3 import write as s3_write
from luzidos_utils.aws_io.db import read as db_read
import boto3
from email.message import EmailMessage
import base64
from email.parser import BytesParser
from email import policy
import email
from email import encoders
from email.utils import parseaddr, formataddr, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime

def _format_address(address):
    name, email = parseaddr(address)
    if not name:
        name = email.split('@')[0]  # Use the local part of the email if no name is provided
    return formataddr((name, email))

def _get_email_body(msg):
    """Extract the plain text/HTML body from the original email."""
    if msg.is_multipart():
        # multipart emails can have text/plain and text/html parts
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # look for the text parts
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                return part.get_payload(decode=True).decode()  # decode from bytes to string
            elif ctype == 'text/html' and 'attachment' not in cdispo:
                return part.get_payload(decode=True).decode()  # HTML part
    else:
        # not multipart - i.e. plain text, no attachments, keeping it simple
        return msg.get_payload(decode=True).decode()

def _update_email_s3(email_details):
    name, sender = parseaddr(email_details['sender'])
    recipients = email_details['recipients']
    subject = email_details['subject']
    date = email_details['date']
    body = email_details['body']
    thread_id = email_details['thread_id']
    message_id = email_details['message_id']

    userSub = db_read.get_user_from_db(sender)
    if userSub is None:
        print('Error: User Sub is NONE.')
        return False
    

    s3_email_json = s3_read.read_email_body_from_s3(userSub, thread_id)

    if s3_email_json is not None:
        if s3_email_json['thread_id'] != thread_id:
            print('Error: Thread IDs dont match with S3.')
            return False
        
        new_message = {
            message_id: {
                'workmail_id': None,
                'date': date,
                'Subject': subject,
                'From': sender,
                'To': recipients,
                'body': body,
            }
        }

        s3_email_json['messages'].update(new_message)
        email_json = s3_email_json

    else:
        email_json = {
            'thread_id': thread_id,
            'messages': {
                thread_id: {
                    'workmail_id': None,
                    'date': date,
                    'Subject': subject,
                    'From': sender,
                    'To': recipients,
                    'body': body,
                }
            }
        }

    return s3_write.upload_email_body_to_s3(userSub, thread_id, email_json)
    

def send_message(from_address, to_address, subject, body, attachments=None, cc=None, thread_id=None, message_id=None):
    """Create and send an email message
    Print the returned message id
    Returns: Message object, including message id
    """
    
    ses = boto3.client('ses', region_name='us-west-2')

    msg = MIMEMultipart()
    
    # Add email body
    part = MIMEText(body, 'plain')
    msg.attach(part)

    msg['Subject'] = subject
    msg['From'] = _format_address(from_address)
    msg['To'] = _format_address(to_address)

    # Custom Message ID
    message_id = make_msgid(domain='luzidos.com')
    msg['References'] = message_id
    msg['Message-ID'] = message_id

    
    if cc:
        msg['Cc'] = _format_address(cc) # Only one CC, could case problems TODO.

    # Attachments
    if attachments:
        for file_path in attachments:
            bucket_name = file_path.split('/')[0]
            object_name = '/'.join(file_path.split('/')[1:])
            file_data = s3_read.read_file_from_s3(bucket_name, object_name)
            
            part = MIMEBase('application', "octet-stream")
            part.set_payload(file_data)
            encoders.encode_base64(part)
            
            file_name = file_path.split('/')[-1]
            part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
            
            msg.attach(part)

    # Send the email
    try:
        response = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']] + ([cc] if cc else []),
            RawMessage={'Data': msg.as_bytes()}
        )
        print("Email sent! Message ID:", response['MessageId'])

        email_details = {
            'sender':  msg['From'],
            'recipients': [msg['To']] + ([cc] if cc else []),
            'subject':  msg['Subject'],
            'date': str(datetime.now()),  # Example date
            'body': body,
            'message_id': msg['References'],
            'thread_id': msg['References']
        }
        if not _update_email_s3(email_details):
            print("ERROR: Failure to upload email json to S3.")
        
    except Exception as e:
        print("Failed to send email:", e)

    return

def reply_to_message(message_id, body, attachments=None, reply_all=False):
    workmail = boto3.client('workmailmessageflow', region_name='us-west-2')
    ses = boto3.client('ses', region_name='us-west-2')

    # Fetch the original email content from WorkMail using the thread_id (message ID)
    raw_msg = workmail.get_raw_message_content(messageId=message_id)

    # Parse the original email to extract necessary details
    msg = email.message_from_bytes(raw_msg['messageContent'].read(), policy=policy.default)

    # Get body of message.
    msg_body = _get_email_body(msg)
    
    # Extract the 'To' headers and proceed to filter.
    to_header = msg.get('To', ' ')
    recipient_list = to_header.split(',')

    # Filter recipients to find the ones with @luzidos.com
    luzidos_recipients = [
        recipient for recipient in recipient_list
        if parseaddr(recipient)[1].endswith(f'@luzidos.com')
    ]

    num_recipients = len(luzidos_recipients)
    if num_recipients > 1:
        print('Error: too many recipients.')
        return
    elif num_recipients == 0:
        print("Error: No recipients with @luzidos.com found.")
        return 
    
    to_header = luzidos_recipients[0].strip()

    #
    from_header = msg['From']
    cc_header = msg.get('Cc', '')

    message_id = msg['Message-ID']
    references = msg['References']
    subject = msg['Subject']
    in_reply_to = msg['In-Reply-To']

        # Determine thread ID
    if references:
        thread_id = references.split()[0]
    elif in_reply_to:
        thread_id = in_reply_to
    else:
        thread_id = message_id

    # Carranza magic touch
    if not in_reply_to:
        in_reply_to = message_id

    print("To: ", to_header)
    print("From: ", from_header)
    print("Message ID: ", message_id)
    print("References: ", references)
    print("Subject: ", subject)
    print("In Reply To: ", in_reply_to)

    # Construct the new email message
    new_msg = MIMEMultipart()
    new_msg['Subject'] = subject
    new_msg['From'] = to_header  # This should be your email if you are the sender
    new_msg['To'] = from_header
    new_msg['In-Reply-To'] = in_reply_to

    # Custom message ID for outbound emails.
    new_msg['Message-ID'] = make_msgid(domain='luzidos.com')

    if references:
        new_msg['References'] = references + ' ' + message_id
    else:
        new_msg['References'] = message_id

    # Reply to all CC.
    if reply_all:
        cc_list = [cc_header, to_header]
        cc = ', '.join(filter(None, cc_list))  # Remove empty strings and join
    else:
        cc = None

    print('New References: ', new_msg['References'])
    print('New In Reply To: ', new_msg['In-Reply-To'])

    # Construct body.
    full_body = f"{body}\r\n\r\n{msg_body}"
    part = MIMEText(full_body, 'plain')
    new_msg.attach(part)

    # Add attachments
    if attachments:
        for file_path in attachments:
            bucket_name = file_path.split('/')[0]
            object_name = '/'.join(file_path.split('/')[1:])
            file_data = s3_read.read_file_from_s3(bucket_name, object_name)
            
            part = MIMEBase('application', "octet-stream")
            part.set_payload(file_data)
            encoders.encode_base64(part)
            
            file_name = file_path.split('/')[-1]
            part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
            
            new_msg.attach(part)


    try:
        # Send the email using SES
        response = ses.send_raw_email(
            Source=new_msg['From'],  # Make sure this is a valid "from" address that you control
            Destinations=[new_msg['To']] + ([cc] if cc else []),
            RawMessage={'Data': new_msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])

        email_details = {
            'sender': new_msg['From'],
            'recipients': [new_msg['To']] + ([cc] if cc else []),
            'subject':  new_msg['Subject'],
            'date': str(datetime.now()),  # Example date
            'body': full_body,
            'message_id': new_msg['Message-ID'],
            'thread_id': thread_id
        }

        if not _update_email_s3(email_details):
            print("ERROR: Failure to upload email json to S3.")
    except Exception as e:
        print("Failed to send email:", e)
        
    return


if __name__ == "__main__":
    # Test (Get ID from CloudWatchlogs)
    # send_message(
    #     from_address='luzidos@luzidos.com',
    #     to_address='tiberiomalaiud@gmail.com',
    #     subject='Caleb Test',
    #     body='Will it work?',
    #     #attachments=[{'filename': 'test.txt', 'content': 'SGVsbG8gd29ybGQ='}],  
        
    # )

    # Outlook 658cfeaf-c157-3f57-9e7d-44bc12446f1c
    # Gmail cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e
    # Outlook 25102b05-7c2c-34fb-96a3-703a08a89336

    reply_to_message(message_id="15478ae3-1628-3657-8f97-d62615556204", body='I call cap Daniel.') 
    
