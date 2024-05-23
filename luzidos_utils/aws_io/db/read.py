import boto3
from botocore.exceptions import ClientError

def read_from_dynamodb(email):
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # Select your table
    table = dynamodb.Table('emailToUserId')

    # Get the item from the table
    try:
        response = table.get_item(
            Key={
                'email': email
            }
        )
        if 'Item' in response:
            return response['Item'].get('value')
        else:
            print(f"No item found with email: {email}")
            return None
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    

if __name__ == "__main__":
    # Test here.
    #print(read_from_dynamodb('luzidos@luzidos.com'))