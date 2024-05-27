from luzidos_utils.aws_io.s3 import read as s3_read
import boto3
from email.message import EmailMessage
import base64
from email.parser import BytesParser
from email import policy
import email
import re
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def _format_address(address):
    name, email = parseaddr(address)
    if not name:
        name = email.split('@')[0]  # Use the local part of the email if no name is provided
    return formataddr((name, email))


def send_message(from_address, to_address, subject, body, attachments=None, cc=None, thread_id=None, message_id=None):
    """Create and send an email message
    Print the returned message id
    Returns: Message object, including message id
    """
    
    ses = boto3.client('ses', region_name='us-west-2')

    msg = EmailMessage()
    msg.set_content(body)

    msg['Subject'] = subject
    msg['From'] = _format_address(from_address)
    msg['To'] = _format_address(to_address)

    if cc:
        msg['Cc'] = _format_address(cc)


    # Set In-Reply-To and References headers for threading
    msg['In-Reply-To'] = message_id
    if thread_id:
        msg['References'] = thread_id + ' ' + message_id
    else:
        msg['References'] = message_id

    if attachments:
        for file_path in attachments:
            bucket_name = file_path.split('/')[0]
            file_name = file_path.split('/')[-1]
            object_name = '/'.join(file_path.split('/')[1:])
            file_data = s3_read.read_file_from_s3(bucket_name, object_name)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    # Send the email
    try:
        # Convert message to string and send via SES
        raw_data = msg.as_bytes()
        if thread_id:
            raw_data["threadId"] = thread_id
        response = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']] + ([cc] if cc else []),
            RawMessage={'Data': raw_data}
        )
        print("Email sent! Message ID:", response['MessageId'])
        return message_id
    except Exception as e:
        print("Failed to send email:", e)


def reply_to_message(message_id, body, attachments=None, reply_all=False):
    workmail = boto3.client('workmailmessageflow', region_name='us-west-2')
    ses = boto3.client('ses', region_name='us-west-2')

    # Fetch the original email content from WorkMail using the thread_id (message ID)
    raw_msg = workmail.get_raw_message_content(messageId=message_id)

    # Parse the original email to extract necessary details
    msg = email.message_from_bytes(raw_msg['messageContent'].read(), policy=policy.default)

    headers = {key: value for key, value in msg.items()}
    
    # Extract the 'To' and 'From' headers
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
    from_header = msg['From']
    message_id = msg['Message-ID']
    references = msg['References']
    subject = msg['Subject']
    in_reply_to = msg['In-Reply-To']
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
    new_msg['Subject'] = 'Re: ' + subject
    new_msg['From'] = to_header  # This should be your email if you are the sender
    new_msg['To'] = from_header
    new_msg['In-Reply-To'] = in_reply_to
    if references:
        message_ids = references.split()
        thread_id = message_ids[0] if message_ids else None
        new_msg['References'] = references + ' ' + message_id
    else:
        new_msg['References'] = message_id

    if reply_all:
        cc = headers.get('To', '') + ', ' + headers.get('Cc', '')
    else:
        cc = None

    print('New References: ', new_msg['References'])
    print('New In Reply To: ', new_msg['In-Reply-To'])
    # send_message(
    #     from_address=to_header,
    #     to_address=from_header,
    #     subject=subject,
    #     body=body, 
    #     attachments=attachments,
    #     cc=cc, 
    #     thread_id=thread_id,
    #     message_id=message_id
    # )
    # return
    # new_msg.set_content(body)
    part = MIMEText(body, 'plain')
    new_msg.attach(part)


    # Send the email using SES
    response = ses.send_raw_email(
        Source=to_header,  # Make sure this is a valid "from" address that you control
        Destinations=[from_header],
        RawMessage={'Data': new_msg.as_string()}
    )
  
    return





if __name__ == "__main__":
    # Example usage
    # send_message(
    #     from_address='luzidos@luzidos.com',
    #     to_address='acarrnza@stanford.edu',
    #     subject='Pendejito Supremo',
    #     body='Que genio andres caradfnasdnza.',
    #     #attachments=[{'filename': 'test.txt', 'content': 'SGVsbG8gd29ybGQ='}],  
        
    # )

    # Outlook b729e81f-387b-3f05-9557-026fe1aa4afa
    # Gmail cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e
    # Outlook 25102b05-7c2c-34fb-96a3-703a08a89336

    reply_to_message(message_id="1e68a6d7-daea-3571-ab1d-2525c98c0c9e", body='Andres es un pendejo.') 
    #reply_to_message(thread_id="d0a9b311-eff9-379a-bebe-8bee27219036", body="What is this?")
    #reply_to_message(thread_id="cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e", body='New email.') 
    #reply_to_message(thread_id="25102b05-7c2c-34fb-96a3-703a08a89336", body='We are testing people. ') 


    # reply_to_message(
    #     message_id="cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e",
    #     body='This is a reply from luzidos.',
    #     attachments=None,
    #     reply_all=False
    # )
