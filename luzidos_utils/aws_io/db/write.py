import requests
import boto3
from botocore.exceptions import ClientError

def update_invoice_status(user_id, invoice_id, status):
    url = 'https://b7843zphhl.execute-api.us-west-2.amazonaws.com/prod'  
    headers = {
        'x-api-key': 'CVsju5YkVA68kGdcAATjL6GjXxdYbxjr6Nhp9L2L' 
    }
    body = {
        "operation": "m.odify",
        "data": {
            "userID": user_id,
            "invoiceID": invoice_id,
            "statusOfTransaction": status
        }
    }
    
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        return 'Entry status updated successfully'
    else:
        # Handle potential error cases here depending on how you want to deal with them
        return 'Error updating entry status', response.status_code
    

def add_email_and_user_to_db(email, value):
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Select your table
    table = dynamodb.Table('emailToUserId')

    # Put the item into the table
    try:
        response = table.put_item(
            Item={
                'email': email,
                'value': value
            }
        )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None


    
    
    
    
    