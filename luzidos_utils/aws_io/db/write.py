import requests
import boto3
from botocore.exceptions import ClientError


def add_invoice(user_id, invoice_id, vendor_name, transaction_items, transaction_total, transaction_datetime, transaction_status):
     # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Select your table
    table = dynamodb.Table('invoiceTable-staging')

    # Put the item into the table
    try:
        response = table.put_item(
            Item={
                "userID": user_id,
                "invoiceID": invoice_id,
                "vendorName": vendor_name,
                "transactionItems": transaction_items,
                "transactionTotal": transaction_total,
                "transactionDatetime": transaction_datetime,
                "transactionStatus": transaction_status,
            }
        )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

def update_invoice_status(user_id, invoice_id, status):
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Select your table
    table = dynamodb.Table('invoiceTable-staging')

    # Update the item in the table
    try:
        response = table.update_item(
            Key={
                "userID": user_id,
                "invoiceID": invoice_id
            },
            UpdateExpression="SET transactionStatus = :status",
            ExpressionAttributeValues={
                ":status": status
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

    

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

if __name__ == "__main__":
    #update_invoice_status("927aa041-e5ba-4acf-ab0e-19a1c629bee9", "Test", "Incomplete!")
    add_invoice(
        "927aa041-e5ba-4acf-ab0e-19a1c629bee9",
        "Test",
        "Carranza el Pajero",
        [],
        12000,
        "2024-03-10T19:20:02.708841",
        "Pending"
    )
    
    
    
    