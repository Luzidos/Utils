from luzidos_utils.aws_io.s3 import read as s3_read
import boto3
from email.message import EmailMessage
import base64
from email.parser import BytesParser
from email import policy
import email
import re
from email.utils import parseaddr, formataddr

def _format_address(address):
    name, email = parseaddr(address)
    if not name:
        name = email.split('@')[0]  # Use the local part of the email if no name is provided
    return formataddr((name, email))


def send_message(from_address, to_address, subject, body, attachments=None, cc=None):
    """Create and send an email message
    Print the returned message id
    Returns: Message object, including message id
    """
    
    ses = boto3.client('ses', region_name='us-west-2')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = _format_address(from_address)
    msg['To'] = _format_address(to_address)

    if cc:
        msg['Cc'] = _format_address(cc)

    # Include the email body
    msg.set_content(body)

    # Handle attachments
    if attachments:
        for attachment in attachments:
            with open(attachment['path'], 'rb') as f:
                msg.add_attachment(f.read(), maintype='application',
                                   subtype='octet-stream', filename=attachment['filename'])

    # Send the email
    try:
        # Convert message to string and send via SES
        raw_data = msg.as_bytes()
        response = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']] + ([cc] if cc else []),
            RawMessage={'Data': raw_data}
        )
        message_id = response['MessageId']
        print("Email sent! Message ID:", message_id)
        return message_id
    except Exception as e:
        print("Failed to send email:", e)


def reply_to_message(message_id, body, attachments=None, reply_all=False):
    """Reply to an existing email thread using AWS WorkMail and SES."""
    
    # Initialize AWS clients for WorkMail and SES
    workmail = boto3.client('workmailmessageflow', region_name='us-west-2')
    ses = boto3.client('ses', region_name='us-west-2')
    
    # Fetch the original email content from WorkMail using the thread_id (message ID)
    raw_msg = workmail.get_raw_message_content(messageId=message_id)
    
    # Parse the original email to extract necessary details
    msg = email.message_from_bytes(raw_msg['messageContent'].read(), policy=policy.default)

    original_date = msg.get('Date', '')
    original_subject = msg.get('Subject', '')
    original_sender = msg.get('From', '')
    original_recipients = msg.get('To', '')

    # Filter recipients to find the ones with @luzidos.com
    recipient_list = original_recipients.split(',')

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

    original_references = msg.get('References', '')
    original_in_reply_to = msg.get('In-Reply-To', '')
    original_message_id = msg.get('Message-ID', '')

    print("Original Date:", original_date)
    print('Original Subject:', original_subject)
    print('Original Sender:', original_sender)
    print('Original Recipients:', original_recipients)
    print('Original References:', original_references)
    print('Original In reply to:', original_in_reply_to)
    print('Original Message ID:', original_message_id)
    # print('Luzidos Recipients:', luzidos_recipients)

        # Validate and format the 'To' header
    to_name, to_email = parseaddr(luzidos_recipients[0])
    if not to_name:
        to_name = to_email.split('@')[0]  # Use the local part of the email if no name is provided
    formatted_to_header = formataddr((to_name, to_email))

    print("Formatted To:", formatted_to_header)
    
    # Create a reply email
    reply_email = EmailMessage()
    reply_email['Subject'] = 'Re: ' + original_subject
    reply_email['From'] = formatted_to_header  # Use the original recipient as the sender for the reply
    reply_email['To'] = original_sender  # Reply to the original sender


    # Set In-Reply-To and References headers for threading
    reply_email['In-Reply-To'] = original_message_id
    if original_references:
        reply_email['References'] = original_references + ' ' + original_message_id
    else:
        reply_email['References'] = original_message_id
    
    reply_email.set_content(body)

    # Handle 'Reply All'
    if reply_all:
        reply_email['Cc'] = msg.get('Cc', '')

    # Attach files if any
    if attachments:
        for attachment in attachments:
            with open(attachment['path'], 'rb') as f:
                reply_email.add_attachment(f.read(), maintype='application',
                                           subtype='octet-stream', filename=attachment['filename'])

    # Encode the message to base64 and send it via SES

    raw_data = base64.b64encode(reply_email.as_bytes()).decode('utf-8')
    print('From reply email.', reply_email['From'])
    try:
        response = ses.send_raw_email(
            Source="luzidos <luzidos@luzidos.com>",
            Destinations=[original_sender] + ([msg.get('Cc')] if reply_all and 'Cc' in msg else []),
            RawMessage={'Data': raw_data}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Failed to send email:", e)





def test(thread_id, body):
    workmail = boto3.client('workmailmessageflow', region_name='us-west-2')
    ses = boto3.client('ses', region_name='us-west-2')

    # Fetch the original email content from WorkMail using the thread_id (message ID)
    raw_msg = workmail.get_raw_message_content(messageId=thread_id)

    # Parse the original email to extract necessary details
    msg = email.message_from_bytes(raw_msg['messageContent'].read(), policy=policy.default)

    headers = {key: value for key, value in msg.items()}
    print(headers)

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


    print("To: ", to_header)
    print("From: ", from_header)
    print("Message ID: ", message_id)
    print("References: ", references)
    print("Subject: ", subject)
    print("In Reply To: ", in_reply_to)

    # Construct the new email message
    new_msg = EmailMessage()
    new_msg['Subject'] = subject
    new_msg['From'] = to_header  # This should be your email if you are the sender
    new_msg['To'] = from_header

    # Set In-Reply-To and References headers for threading
    new_msg['In-Reply-To'] = message_id
    if references:
        new_msg['References'] = references + ' ' + message_id
    else:
        new_msg['References'] = message_id

    print('New References: ', new_msg['References'])
    print('New In Reply To: ', new_msg['In-Reply-To'])

    new_msg.set_content(body)

    # Send the email using SES
    response = ses.send_raw_email(
        Source=to_header,  # Make sure this is a valid "from" address that you control
        Destinations=[from_header],
        RawMessage={'Data': new_msg.as_bytes()}
    )
  

    print("Email sent! Message ID:", response)

# Example call
# test('example_thread_id', 'This is a reply.')



if __name__ == "__main__":
    # Example usage
    # send_message(
    #     from_address='luzidos@luzidos.com',
    #     to_address='tiberiom@stanford.edu',
    #     subject='Hello World from CLI',
    #     body='This is a test email sent from Luzidos.',
    #     # attachments=[{'filename': 'test.txt', 'content': 'SGVsbG8gd29ybGQ='}],  
        
    # )

    # Outlook b729e81f-387b-3f05-9557-026fe1aa4afa
    # Gmail cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e
    # Outlook 25102b05-7c2c-34fb-96a3-703a08a89336

    #test(thread_id="b729e81f-387b-3f05-9557-026fe1aa4afa", body='We are testing people. ') 
    test(thread_id="d0a9b311-eff9-379a-bebe-8bee27219036", body="What is this?")
    #test(thread_id="cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e", body='New email.') 
    #test(thread_id="25102b05-7c2c-34fb-96a3-703a08a89336", body='We are testing people. ') 


    # reply_to_message(
    #     message_id="cbb54c08-4ad9-3f0f-a578-ae4bfb905c4e",
    #     body='This is a reply from luzidos.',
    #     attachments=None,
    #     reply_all=False
    # )
