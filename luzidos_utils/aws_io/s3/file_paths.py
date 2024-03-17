# Description: File paths for S3 bucket.
ROOT_BUCKET = "luzidosdatadump"

#invoice object path
INVOICE_DIR_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/"
INVOICE_FILE_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/files/{file_name}"
INVOICE_DATA_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/{file_name}.json"
INVOICE_EINVOICE_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/files/einvoice.pdf"
INVOICE_LOCKED_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/is_locked.json"
INVOICE_LOG_PATH = "private/{user_id}/invoices/invoice_{invoice_id}/state_logs.json"

# Email object path
EMAIL_DIR_PATH = "private/{user_id}/emails/email_{email_id}/"
EMAIL_JSON_PATH = "private/{user_id}/emails/email_{email_id}/email.json"
EMAIL_ATTACHMENT_DIR_PATH = "private/{user_id}/emails/email_{email_id}/attachments/"
EMAIL_ATTACHMENT_PATH = "private/{user_id}/emails/email_{email_id}/attachments/{attachment_name}"

# user object path
USER_DATA_PATH = "private/{user_id}/user/user_data.json"
USER_AGENT_PROCESSES_PATH = "private/{user_id}/user/agent_processes.json"