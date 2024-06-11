# Description: File paths for S3 bucket.
ROOT_BUCKET = "luzidosdatadump"

#invoice object path
INVOICE_DIR_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/"
INVOICE_FILE_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/files/{file_name}"
INVOICE_DATA_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/{file_name}.json"
INVOICE_EINVOICE_FILE_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/files/einvoice.pdf"
INVOICE_EINVOICE_DATA_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/files/einvoice.json"
INVOICE_LOCKED_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/is_locked.json"
INVOICE_LOG_PATH = "public/{user_id}/invoices/invoice_{invoice_id}/log.json"

# Email object path
EMAIL_DIR_PATH = "public/{user_id}/emails/email_{email_id}/"
EMAIL_JSON_PATH = "public/{user_id}/emails/email_{email_id}/email.json"
EMAIL_ATTACHMENT_DIR_PATH = "public/{user_id}/emails/email_{email_id}/attachments/"
EMAIL_ATTACHMENT_PATH = "public/{user_id}/emails/email_{email_id}/attachments/{attachment_name}"


# user object path
USERS_DIR_PATH = "public/{user_id}/user/"
USER_DATA_PATH = "public/{user_id}/user/user_data.json"
USER_AGENT_PROCESSES_PATH = "public/{user_id}/user/agent_processes.json"
USER_EMAIL_CREDENTIALS_PATH = "public/{user_id}/user/email_credentials.json"
USER_EMAIL_TOKEN_PATH = "public/{user_id}/user/email_token.json"
USER_CEDULA_PATH = "public/{user_id}/user/cedula.pdf"
USER_RUT_PATH = "public/{user_id}/user/rut.pdf"

def USER_ID_DOCUMENT_PATH(id_document_type):
    if id_document_type.lower() == "cedula":
        return f"{ROOT_BUCKET}/{USER_CEDULA_PATH}"
    elif id_document_type.lower() == "rut":
        return f"{ROOT_BUCKET}/{USER_RUT_PATH}"
    else:
        raise ValueError(f"Invalid id_document_type: {id_document_type}")