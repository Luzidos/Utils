from os import read
import boto3
import json
import uuid
from botocore.exceptions import ClientError
from luzidos_utils.aws_io.s3 import file_paths as fp
import datetime as dt
from luzidos_utils.aws_io.s3 import read as s3_read
from luzidos_utils.constants.state import INIT, COMPLETE

#constants
BUCKET_NAME = "luzidosdatadump"
ROOT_INVOICE_PATH = "invoices/invoice"
ROOT_EMAIL_PATH = "emails/email"
ROOT_USER_PATH = 'userid'

"""
WRITE UTILS
"""
def upload_file_to_s3(bucket_name, file_path, object_name):
    """
    Upload a file to an S3 bucket

    :param bucket_name: Bucket to upload to
    :param file_path: File to upload
    :param object_name: S3 object name
    :return: True if file was uploaded, else False
    """

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
    except Exception as e:
        print(e)
        return False
    return True

def upload_file_obj_to_s3(bucket_name, file_obj, object_name):
    """
    Upload a file object to an S3 bucket

    :param bucket_name: Bucket to upload to
    :param file_obj: File object
    :param object_name: S3 object name
    :return: True if file was uploaded, else False
    """

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
    except Exception as e:
        print(e)
        return False
    return True

def upload_email_attachment_to_s3(user_id, email_id, file_obj, attachment_name):
    """
    Upload an email attachment to an S3 bucket

    :param user_id: User id
    :param file_obj: File object
    :param attachment_name: S3 object name
    :return: True if file was uploaded, else False
    """
    object_name = fp.EMAIL_ATTACHMENT_PATH.format(user_id=user_id, email_id=email_id, attachment_name=attachment_name)
    status = upload_file_obj_to_s3(fp.ROOT_BUCKET, file_obj, object_name)
    return status

def upload_email_attachment_json_to_s3(user_id, email_id, attachment_name, attachment_data):
    """
    Upload an email attachment to an S3 bucket

    :param user_id: User id
    :param file_obj: File object
    :param attachment_name: S3 object name
    :return: True if file was uploaded, else False
    """
    object_name = fp.EMAIL_ATTACHMENT_PATH.format(user_id=user_id, email_id=email_id, attachment_name=attachment_name)
    status = upload_dict_as_json_to_s3(fp.ROOT_BUCKET, attachment_data, object_name)
    return status


def upload_email_body_to_s3(user_id, thread_id, email_body):
    """
    Upload email body to S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param email_body: Email body
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.EMAIL_BODY_JSON_PATH.format(user_id=user_id, email_id=thread_id)
    status = upload_dict_as_json_to_s3(bucket_name, email_body, object_name)
    return status


def upload_dict_as_json_to_s3(bucket_name, dict_data, object_name):
    """
    Upload a dictionary as a JSON object to an S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param dict_data: Dictionary to upload
    :param object_name: Object name in S3 bucket
    """
    s3_client = boto3.client('s3')

    # Convert dictionary to JSON string
    json_string = json.dumps(dict_data)

    try:
        # Upload the JSON string as an S3 object
        s3_client.put_object(Body=json_string, Bucket=bucket_name, Key=object_name)
        print(f"File uploaded successfully to {bucket_name}/{object_name}")
    except Exception as e:
        print(e)
        return False
    return True

def upload_invoice_data_to_s3(user_id, invoice_id, invoice_data, data_type):
    """
    Upload invoice data to S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_data: Invoice data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_DATA_PATH.format(user_id=user_id, invoice_id=invoice_id, data_type=data_type)
    status = upload_dict_as_json_to_s3(bucket_name, invoice_data, object_name)
    return status

def update_invoice_data_in_s3(user_id, invoice_id, new_invoice_data, data_type):
    """
    Update invoice data in S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :param new_invoice_data: New invoice data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_DATA_PATH.format(user_id=user_id, invoice_id=invoice_id, file_name=data_type)
    invoice_data = s3_read.read_invoice_data_from_s3(user_id, invoice_id, data_type)
    invoice_data.update(new_invoice_data)
    status = upload_dict_as_json_to_s3(bucket_name, invoice_data, object_name)
    return status

def update_invoice_state_in_s3(user_id, invoice_id, new_state):
    """
    Update invoice data in S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :param new_invoice_data: New invoice data
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = f"{ROOT_USER_PATH}-{user_id}/{ROOT_INVOICE_PATH}-{invoice_id}/state-{invoice_id}.json"
    state = s3_read.read_invoice_state_from_s3(user_id, invoice_id)
    state.update(new_state)
    status = upload_dict_as_json_to_s3(bucket_name, state, object_name)
    return status

def update_invoice_state_field_in_s3(user_id, invoice_id, key, value):
    """
    Update invoice state field in S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :param key: Key to update. formated as "key1/key2/.../keyN"
    :param value: New value
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = f"{ROOT_USER_PATH}-{user_id}/{ROOT_INVOICE_PATH}-{invoice_id}/state-{invoice_id}.json"
    state = s3_read.read_invoice_state_from_s3(user_id, invoice_id)

    # Update the state field
    substate = state
    keys = key.split("/")
    for i, subkey in enumerate(keys):
        if i == len(keys) - 1:
            substate[subkey] = value
        else:
            substate = substate[subkey]

    status = upload_dict_as_json_to_s3(bucket_name, state, object_name)
    return status
def update_invoice_state_fields_in_s3(user_id, invoice_id, data):
    """
    Update invoice state field in S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :param key: Key to update. formated as "key1/key2/.../keyN"
    :param value: New value
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = f"{ROOT_USER_PATH}-{user_id}/{ROOT_INVOICE_PATH}-{invoice_id}/state-{invoice_id}.json"
    state = s3_read.read_invoice_state_from_s3(user_id, invoice_id)
    
    # Update the state field
    substate = state
    keys = key.split("/")
    for key, value in data.items():
        for i, subkey in enumerate(keys):
            if i == len(keys) - 1:
                substate[subkey] = value
            else:
                substate = substate[subkey]

    status = upload_dict_as_json_to_s3(bucket_name, state, object_name)
    return status

def update_invoice_contact_in_s3(user_id, invoice_id, new_contact, primary_contact=False, pop_first_alternate=False):
    """
    Update invoice contact in S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param invoice_id: Invoice id
    :param new_contact: New contact
    :param primary_contact: True if new contact is primary contact, else False
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_DATA_PATH.format(user_id=user_id, invoice_id=invoice_id, file_name="transaction")
    transaction_json = s3_read.read_invoice_data_from_s3(bucket_name, user_id, invoice_id, "transaction")
    if primary_contact:
        old_contact = transaction_json["vendor_details"]["vendor_email"]
        transaction_json["vendor_details"]["vendor_email"] = new_contact
        transaction_json["vendor_details"]["additional_vendor_contacts"].append({"vendor_email": old_contact, "status": "WRONG_CONTACT"})
    else:
        transaction_json["vendor_details"]["additional_vendor_contacts"].append({"vendor_email": new_contact, "status": "UNCHECKED_CONTACT"})
    if pop_first_alternate:
        transaction_json["vendor_details"]["additional_vendor_contacts"] = transaction_json["vendor_details"]["additional_vendor_contacts"][1:]
    status = upload_dict_as_json_to_s3(bucket_name, transaction_json, object_name)
    return status


def upload_invoice_file_to_s3(file_path, user_id, invoice_id, file_name):
    """
    Upload invoice file to S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param file_path: File path
    :param invoice_id: Invoice id
    :return: True if file was uploaded, else False
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_FILE_PATH.format(user_id=user_id, invoice_id=invoice_id, file_name=file_name)
    status = upload_file_to_s3(bucket_name, file_path, object_name)
    return status

def generate_invoice_id(invoice_id=None):
    """
    Generate invoice id

    :param invoice_id: Invoice id
    :return: Invoice id
    """
    if invoice_id is None:
        return str(uuid.uuid4())
    else:
        return invoice_id

def copy_file(bucket_name, source_file, dest_file):
    """
    Copy a file from one location to another in an S3 bucket

    :param bucket_name: Name of the S3 bucket
    :param source_file: Source file
    :param dest_file: Destination file
    :return: True if file was copied, else False
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.copy_object(Bucket=bucket_name, CopySource=source_file, Key=dest_file)
    except Exception as e:
        print(e)
        return False
    return True

def copy_einvoice_to_invoice_dir(user_id, invoice_id, einvoice_filename):
    """
    Copy einvoice to invoice directory in S3 bucket

    :param user_id: User id
    :param invoice_id: Invoice id
    :param einvoice_filename: Einvoice filename
    """
    bucket_name = fp.ROOT_BUCKET
    source_file = fp.EMAIL_ATTACHMENT_PATH.format(user_id=user_id, email_id=invoice_id, attachment_name=einvoice_filename)
    dest_file = fp.INVOICE_EINVOICE_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = copy_file(bucket_name, source_file, dest_file)
    return status

def lock_agent(user_id, invoice_id):
    """
    Lock agent execution

    :param user_id: User id
    :param invoice_id: Invoice id
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_LOCK_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, {"locked": True}, object_name)
    return status

def unlock_agent(user_id, invoice_id):
    """
    Unlock agent execution

    :param user_id: User id
    :param invoice_id: Invoice id
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_LOCK_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, {"locked": False}, object_name)
    return status

def log_state(user_id, invoice_id, actor, state_data):
    update_time = dt.datetime.now().isoformat()
    log_entry = {
        "actor": actor,
        "update_time": update_time,
        "state_data": state_data
    }
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_LOG_PATH.format(user_id=user_id, invoice_id=invoice_id)
    state_log = s3_read.read_json_from_s3(bucket_name, object_name)
    state_log["state_log"].append(log_entry)
    status = upload_dict_as_json_to_s3(bucket_name, state_log, object_name)
    return status

# status can be INIT COMPLETE CANCEL
# we should make this a constant
def update_agent_processes(user_id, invoice_id, status=INIT):
    """
    Update open agent processes for a user

    :param user_id: User id
    :param invoice_id: Invoice id
    :param action: Action to perform
    """
    agent_processes = s3_read.read_agent_processes_from_s3(user_id)
    if status == INIT:
        agent_processes["open_agent_processes"].append(invoice_id)
    elif status == COMPLETE:
        agent_processes["open_agent_processes"].remove(invoice_id)
        agent_processes["completed_agent_processes"].append(invoice_id)
    else:
        raise ValueError(f"Invalid status: {status}")
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_AGENT_PROCESSES_PATH.format(user_id=user_id)
    status = upload_dict_as_json_to_s3(bucket_name, agent_processes, object_name)
    return status

def upload_email_token_to_s3(user_id, creds):
    """
    Upload email credentials to S3 bucket

    :param user_id: User id
    :param email_credentials: Email credentials
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.USER_EMAIL_TOKEN_PATH.format(user_id=user_id)
    status = upload_dict_as_json_to_s3(bucket_name, creds, object_name)
    return status

def init_agent(user_id, invoice_id, init_state):
    """
    Initialize agent

    :param user_id: User id
    :param invoice_id: Invoice id
    :param init_state: Initial state
    """
    bucket_name = fp.ROOT_BUCKET

    # create state_log file
    object_name = fp.INVOICE_LOG_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, {"state_log": []}, object_name)

    # create is_locked.json file and initialize it to False
    object_name = fp.INVOICE_LOCKED_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, {"locked": False}, object_name)

    # update agent_processes.json
    status = update_agent_processes(user_id, invoice_id, INIT)

    object_name = fp.INVOICE_STATE_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, init_state, object_name)

    log_state(user_id, invoice_id, "INIT_INVOICE_AGENT_LAMBDA", init_state)
    return status

def write_invoice_state_to_s3(user_id, invoice_id, state):
    """
    Write invoice state to S3 bucket

    :param user_id: User id
    :param invoice_id: Invoice id
    :param state: Invoice state
    """
    bucket_name = fp.ROOT_BUCKET
    object_name = fp.INVOICE_STATE_PATH.format(user_id=user_id, invoice_id=invoice_id)
    status = upload_dict_as_json_to_s3(bucket_name, state, object_name)
    return status

