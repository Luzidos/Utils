import json
import boto3
import email
from email import policy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import BytesParser
from email.mime.base import MIMEBase
from email import encoders

def parse_attachments(email_content):
    print("Starting to parse attachments...")
    msg = BytesParser(policy=policy.default).parsebytes(email_content)
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = part.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                filename = part.get_filename()
                payload = part.get_payload(decode=True)
                attachments.append({'filename': filename, 'content': payload})
                print(f"Attachment {filename} parsed.")
    return attachments


def parse_email_headers(raw_email_content):
    msg = email.message_from_bytes(raw_email_content, policy=policy.default)
    in_reply_to = msg['In-Reply-To']
    references = msg['References']
    subject = msg['Subject']
    print("Extracted In-Reply-To:", in_reply_to)
    print("Extracted References:", references)
    return in_reply_to, references, subject

def lambda_handler(message_id, context):

    
    
    workmail = boto3.client('workmailmessageflow',region_name='us-west-2')
    raw_msg = workmail.get_raw_message_content(messageId=message_id)
    email_content = raw_msg['messageContent'].read()

    

    # Parse email for headers and attachments
    in_reply_to, references, subject = parse_email_headers(email_content)
    attachments = parse_attachments(email_content)

    from_address = 'luzidos@luzidos.com'
    to_address = 'acarrnza@stanford.edu'
    if subject.startswith('Re: '):
        subject = subject
    else:
        subject = 'Re: ' + subject
    body_text = "Thank you for your email. Here is our response."

    send_email_response(from_address, to_address, subject, body_text, in_reply_to, references, attachments)

    return {
        'statusCode': 200,
        'body': json.dumps('Email processed and response sent successfully')
    }

def send_email_response(from_address, to_address, subject, body_text, in_reply_to, references, attachments):
    ses = boto3.client('ses', region_name='us-west-2')
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg['In-Reply-To'] = in_reply_to
    msg['References'] = references

    # Attach the text body
    part = MIMEText(body_text, 'plain')
    msg.attach(part)

    # Attach each file
    for attachment in attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(attachment['content'])
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
        msg.attach(part)

    # Send the email
    try:
        response = ses.send_raw_email(
            Source=from_address,
            Destinations=[to_address],
            RawMessage={'Data': msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Failed to send email:", e)


if __name__ == "__main__":
    lambda_handler(message_id="1e68a6d7-daea-3571-ab1d-2525c98c0c9e", context=None)

# this doesn't work
[
    ('Subject', 'Re: This is a test email hello!'), 
    ('From', '"luzidos@luzidos.com" <luzidos@luzidos.com>'), ('To', 'Andres Carranza <andres.carranza@stanford.edu>'), 
    ('In-Reply-To', '<DS0PR02MB9271F6268B993FF5A48BAC8A80F02@DS0PR02MB9271.namprd02.prod.outlook.com>'), 
    ('References', ' <DS0PR02MB9271F6268B993FF5A48BAC8A80F02@DS0PR02MB9271.namprd02.prod.outlook.com>'), 
    ('Content-Type', 'text/plain; charset="utf-8"'), 
    ('Content-Transfer-Encoding', '7bit'), 
    ('MIME-Version', '1.0')]

# This works
[
    ('Content-Type', 'multipart/mixed; boundary="===============8024294407477304433=="'), 
    ('MIME-Version', '1.0'), 
    ('Subject', 'Re: This is a test email hello!'), 
    ('From', 'luzidos@luzidos.com'), 
    ('To', 'acarrnza@stanford.edu'), 
    ('In-Reply-To', '<DS0PR02MB9271F6268B993FF5A48BAC8A80F02@DS0PR02MB9271.namprd02.prod.outlook.com>'), 
    ('References', '<DS0PR02MB9271F6268B993FF5A48BAC8A80F02@DS0PR02MB9271.namprd02.prod.outlook.com>')
]