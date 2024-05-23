from os import read
import boto3
import json
import uuid
from botocore.exceptions import ClientError
from luzidos_utils.aws_io.s3 import file_paths as fp
import datetime as dt

#constants
BUCKET_NAME = "luzidosdatadump"
ROOT_INVOICE_PATH = "invoices/invoice"
ROOT_EMAIL_PATH = "emails/email"
ROOT_USER_PATH = 'userid'
"""
READ UTILS
"""

def read_file_from_s3(bucket_name, object_name):
    """
    Read a file from an S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param object_name: Object name in S3
    :return: File data
    """
    s3_client = boto3.client('s3')
    try:
        # Get the object from the S3 bucket
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        # Read the object contents
        file_data = response['Body'].read()
        print(f"File read successfully from {bucket_name}/{object_name}")
    except Exception as e:
        print(e, f"\nFile not found in {bucket_name}/{object_name}")
        return None
    return file_data

def file_exists_in_s3(bucket_name, object_name):
    """
    Check if a file exists in an S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param object_name: Object name in S3
    :return: True if exists, False otherwise
    """
    return read_file_from_s3(bucket_name, object_name) is not None

def read_json_from_s3(bucket_name, object_name):
    """
    Read a json file from an S3 bucket

    :param bucket_name: Bucket to read from
    :param object_name: S3 object name
    :return: json data
    """
    response = read_file_from_s3(bucket_name, object_name)
    if response is None:
        return None
    return json.loads(response)

def read_dir_filenames_from_s3(bucket_name, dir_name):
    """
    Read filenames from a directory in an S3 bucket
    This function is used to read all the filenames in a specific directory in an S3 bucket.
    It returns a list of filenames, including the full path to the file object.
    It returns all files in the directory, including files nested in subdirectories.

    :param bucket_name: Bucket to read from
    :param dir_name: S3 directory name
    :return: List of filenames
    """
    s3_client = boto3.client('s3')
    try:
        # Get the object from the S3 bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=dir_name)
        # Read the object contents
        filenames = [obj['Key'] for obj in response['Contents']]
        print(f"Files read successfully from {bucket_name}/{dir_name}")
    except Exception as e:
        print(e)
        return []
    return filenames

def list_childdirectories(bucket_name, prefix):
    """
    List directories in a specific S3 bucket/prefix.
    This function is used to list all the subdirectories in a specific directory in an S3 bucket.
    It returns a list of subdirectores.
    The subdirectories are returned as strings with the full path to the subdirectory object.
    """

    s3_client = boto3.client('s3')
    subfolders = []
    try: 
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
        for content in response.get('CommonPrefixes', []):
            subfolders.append(content['Prefix'])
    except Exception as e:
        print(e)
    return subfolders

def read_invoice_data_from_s3(user_id, invoice_id, file_name):
    """
    Read invoice data from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :return: Invoice data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_DATA_PATH.format(user_id=user_id, invoice_id=invoice_id, file_name=file_name)
    invoice_data = read_json_from_s3(bucket_name, object_name)
    return invoice_data

def read_invoice_state_from_s3(user_id, invoice_id):
    """
    Read invoice data from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :return: Invoice data
    """
    
    return read_invoice_data_from_s3(user_id, invoice_id, "state")

def read_transaction_data_from_s3(user_id, invoice_id):
    """
    Read transaction data from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :return: Transaction data
    """
    return read_invoice_data_from_s3(user_id, invoice_id, "transaction")
    
def read_einvoice_data_from_s3(user_id, invoice_id):
    """
    Read einvoice data from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :return: Einvoice data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_EINVOICE_DATA_PATH.format(user_id=user_id, invoice_id=invoice_id)
    einvoice_data = read_json_from_s3(bucket_name, object_name)
    return einvoice_data



def read_email_body_from_s3(user_id, thread_id):
    """
    Read email body from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param thread_id: Thread id
    :return: Email body
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.EMAIL_JSON_PATH.format(user_id=user_id, email_id=thread_id)
    email_body = read_json_from_s3(bucket_name, object_name)
    return email_body

def read_email_attachments_from_s3(user_id, thread_id):
    """
    Read email attachments from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param thread_id: Thread id
    :return: Email attachments
    """
    bucket_name = fp.ROOT_BUCKET
    attachment_dir = fp.EMAIL_ATTACHMENT_DIR_PATH.format(user_id=user_id, email_id=thread_id)
    attachment_filenames = read_dir_filenames_from_s3(bucket_name, attachment_dir)
    email_attachments = []
    #only read json files
    for attachment_filename in attachment_filenames:
        if attachment_filename.split(".")[-1] == "json":
            attachment = read_json_from_s3(bucket_name, attachment_filename)
            email_attachments.append(attachment)
    return email_attachments

def read_email_attachment_data_from_s3(user_id, thread_id, attachment_id, read_description=True):
    """
    Read email attachments from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param thread_id: Thread id
    :return: Email attachments
    """
    bucket_name = fp.ROOT_BUCKET
    attachment_path = fp.EMAIL_ATTACHMENT_PATH.format(user_id=user_id, email_id=thread_id, attachment_name=f"{attachment_id}.json")
    email_attachments = []
    attachment_data = read_json_from_s3(bucket_name, attachment_path)
    if read_description:
        return attachment_data["attachment_description"]
    return attachment_data["attachment_OCR"]

def read_email_from_s3(user_id, thread_id, focused_message_id=None):
    """
    Read email from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param thread_id: Thread id
    :return: Email
    """
    # TODO incorporate attachments into each individual email message
    email_body = read_email_body_from_s3(user_id, thread_id)
    if focused_message_id == None:
        focused_message_id = list(email_body["messages"].keys())[-1]
    for message_id in email_body["messages"]:
        email_body["messages"][message_id]["attachments"] = []
        for attachment_id in email_body["messages"][message_id]["attachment_ids"]:
            read_description = focused_message_id != message_id
            attachment_data = read_email_attachment_data_from_s3(user_id, thread_id, attachment_id, read_description=read_description)
            email_body["messages"][message_id]["attachments"].append(attachment_data)

    return email_body

def read_user_data_from_s3(user_id):
    """
    Read user data from S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param user_id: User id
    :return: User data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_DATA_PATH.format(user_id=user_id)
    user_data = read_json_from_s3(bucket_name, object_name)
    return user_data

def get_user_email(user_id):
    """
    Read user Agent Email address from User Data Json

    :param bucket_name: Name of the S3 bucket
    :param user_id: User id
    :return: email Address
    """
    userData = read_user_data_from_s3(user_id)
    if userData and "custom:agentEmail" in userData:
        return userData["custom:agentEmail"]
    return None
        


def is_agent_locked(user_id, invoice_id):
    """
    Check if agent execution is locked

    :param user_id: User id
    :param invoice_id: Invoice id
    :return: True if locked, else False
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_LOCKED_PATH.format(user_id=user_id, invoice_id=invoice_id)
    is_locked_json = read_json_from_s3(bucket_name, object_name)

    return is_locked_json["locked"]

def get_open_agent_processes(user_id):
    """
    Get open agent processes for a user

    :param user_id: User id
    :return: List of open agent processes
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_OPEN_AGENT_PROCESSES_PATH.format(user_id=user_id)
    open_agent_processes = read_json_from_s3(bucket_name, object_name)
    if open_agent_processes is None:
       return []
    return open_agent_processes["open_agent_processes"]

def read_email_credentials_from_s3(user_id):
    """
    Read email credentials from S3 bucket

    :param user_id: User id
    :return: Email credentials
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_EMAIL_CREDENTIALS_PATH.format(user_id=user_id)
    email_credentials = read_json_from_s3(bucket_name, object_name)
    return email_credentials

def read_email_token_from_s3(user_id):
    """
    Read email token from S3 bucket

    :param user_id: User id
    :return: Email token
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_EMAIL_TOKEN_PATH.format(user_id=user_id)
    email_token = read_json_from_s3(bucket_name, object_name)
    return email_token


def read_agent_processes_from_s3(user_id):
    """
    Get agent processes for a user

    :param user_id: User id
    :return: List of agent processes
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_AGENT_PROCESSES_PATH.format(user_id=user_id)
    agent_processes = read_json_from_s3(bucket_name, object_name)
    if agent_processes is None:
        agent_processes = {"open_agent_processes": [], "completed_agent_processes": [], "cancelled_agent_processes": []}
    return agent_processes


def get_all_users():
    """
    Get all users

    :return: List of user ids
    """
    # return list of all user ids
    # user ids are all the subdirectories directly underneath USER_DIR_PATH
    bucket_name = fp.ROOT_BUCKET

    subdirectories = list_childdirectories(bucket_name, "public/")

    user_ids = [subdirectory.split("/")[1] for subdirectory in subdirectories]

    return user_ids
    

if __name__ == "__main__":
    # test read functions
    # print(read_file_from_s3(BUCKET_NAME, "public/1/invoices/invoice_1/files/1.pdf"))
    # print(read_json_from_s3(BUCKET_NAME, "public/1/invoices/invoice_1/files/1.json"))
    print(read_dir_filenames_from_s3(BUCKET_NAME, "public/"))
    print(list_childdirectories(BUCKET_NAME, "public/"))
    # print(read_invoice_data_from_s3(1, 1, "1.json"))
    # print(read_invoice_state_from_s3(1, 1))
    # print(read_transaction_data_from_s3(1, 1))
    # print(read_einvoice_data_from_s3(1, 1))
    # print(read_email_body_from_s3(1, 1))
    # print(read_email_attachments_from_s3(1, 1))
    # print(read_email_attachment_data_from_s3(1, 1, 1))
    # print(read_email_from_s3(1, 1))
    # print(read_user_data_from_s3(1))
    # print(is_agent_locked(1, 1))
    # print(get_open_agent_processes(1))
    # print(read_email_credentials_from_s3(1))
    # print(read_email_token_from_s3(1))
    # print(read_agent_processes_from_s3(1))
    # print(get_all_users())
    pass