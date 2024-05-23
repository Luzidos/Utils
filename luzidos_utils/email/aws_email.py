from luzidos_utils.aws_io.s3 import read as s3_read
import boto3
from email.message import EmailMessage
import base64

# PUBLIC FUNCTIONS
# THESE ARE CALLED BY ANDRES!!!!!

def upload_unread_messages_to_s3(user_id, query):
    """Get messages from the user's mailbox.
    Uploads all of the unread messages to s3 in the format that I chose
    It also uploads all of its relevant attachments to s3
    It also applies ocr to the attachments and uploads the ocr data to s3
    Args:
        query: The query string used to filter messages.  read/unread
    Returns:
        A dictionary of messages.
    """

    # Pseudocode

    # Get the email
    agent_email = s3_read.get_user_email(user_id)

    return

    # Get the unread messages
    # unread_messages = amazone_ses.get_unread_messages(agent_email, query)

    # Upload the unread messages to s3
    # ask andres

    # Upload the attachments to s3
    # ask andres

    # Apply ocr to the attachments
    # ask andres

    # Upload the ocr data to s3
    # ask andres

    # return threads of the unread emails



def send_message(from_address, to_address, subject, body, attachments=None, cc=None, thread_id=None, message_id=None):
    """Create and send an email message
    Print the returned message id
    Returns: Message object, including message id
    """
    
    ses = boto3.client('ses', region_name='us-west-2')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address

    if cc:
        msg['Cc'] = cc

    if message_id:
        msg['In-Reply-To'] = message_id  # Direct reply to this message

    if thread_id:
        # Maintain all previous references and append the current message_id being replied to
        updated_references = f"{thread_id} {message_id}" if thread_id else message_id
        msg['References'] = updated_references.strip()

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
            Source=from_address,
            Destinations=[to_address] + ([cc] if cc else []),
            RawMessage={'Data': raw_data}
        )
        message_id = response['MessageId']
        print("Email sent! Message ID:", message_id)
        return message_id
    except Exception as e:
        print("Failed to send email:", e)


def reply_to_message(thread_id, body, attachments=None, reply_all=False):
    """Reply to an existing email thread using AWS WorkMail and SES."""
    
    # Initialize AWS clients for WorkMail and SES
    workmail = boto3.client('workmailmessageflow', region_name='us-west-2')
    ses = boto3.client('ses', region_name='us-west-2')
    
    # Fetch the original email content from WorkMail using the thread_id (message ID)
    response = workmail.get_raw_message_content(messageId=thread_id)
    raw_email = response['messageContent'].read()
    
    # Parse the original email to extract necessary details
    original_email = EmailMessage()
    original_email.set_content(raw_email)
    
    # Create a reply email
    reply_email = EmailMessage()
    reply_email['Subject'] = 'Re: ' + original_email['Subject']
    reply_email['From'] = original_email['To']  # Reply from the 'To' address of the received email
    reply_email['To'] = original_email['From']
    reply_email.set_content(body)
    
    # Set In-Reply-To and References for threading
    reply_email['In-Reply-To'] = original_email['Message-ID']
    if original_email['References']:
        reply_email['References'] = original_email['References'] + ' ' + original_email['Message-ID']
    else:
        reply_email['References'] = original_email['Message-ID']
    
    # Handle 'Reply All'
    if reply_all and 'Cc' in original_email:
        reply_email['Cc'] = original_email['Cc']
    
    # Attach files if any
    if attachments:
        for attachment in attachments:
            with open(attachment['path'], 'rb') as f:
                reply_email.add_attachment(f.read(), maintype='application',
                                           subtype='octet-stream', filename=attachment['filename'])
    
    # Encode the message to base64 and send it via SES
    raw_data = base64.b64encode(reply_email.as_bytes()).decode('utf-8')
    try:
        response = ses.send_raw_email(
            Source=reply_email['From'],
            Destinations=[reply_email['To']] + ([reply_email['Cc']] if reply_all and 'Cc' in reply_email else []),
            RawMessage={'Data': raw_data}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Failed to send email:", e)


# PRIVATE FUNCTIONS
# THESE ARE HELPER FUNCTIONS THAT ARE CALLED BY THE PUBLIC FUNCTIONS

if __name__ == "__main__":
    print('This is a test. ')
    pass
    # Example usage
    upload_unread_messages_to_s3("927aa041-e5ba-4acf-ab0e-19a1c629bee9", None) # Tiberio User ID

    # send_message(
    #     from_address='tiberio@luzidos.com',
    #     to_address='tiberiomalaiud@gmail.com',
    #     subject='Hello World',
    #     body='This is a test email.',
    #     # attachments=[{'filename': 'test.txt', 'content': 'SGVsbG8gd29ybGQ='}],  
    #     cc='acarrnza@stanford.edu',
    # )

    # reply_to_message(
    #     thread_id='&lt;existing_message_id&gt;',
    #     body='Here is my reply to the email thread.',
    #     attachments=[{'path': '/path/to/document.pdf', 'filename': 'document.pdf'}],
    #     reply_all=True
    # )
