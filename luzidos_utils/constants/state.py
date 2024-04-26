# state constants
SEND_EMAIL = "SEND_EMAIL"
SUCCESFULLY_TERMINATED = "SUCCESFULLY_TERMINATED"
AWAITING_RESPONSE = "AWAITING_RESPONSE"
INCORRECT_CONTACT = "INCORRECT_CONTACT"
PROCESS_EINVOICE = "PROCESS_EINVOICE"
EXTRACT_EMAIL_ACTION = "EXTRACT_EMAIL_ACTION"


# email_response_type constants
GENERIC_FOLLOWUP = "GENERIC_FOLLOWUP"
THANK_YOU_EMAIL = "THANK_YOU_EMAIL"
REQUEST_INVOICE = "REQUEST_INVOICE"
USE_LLM = "USE_LLM"
EMAIL_USER = "EMAIL_USER"
MATCH_EMAIL = "MATCH_EMAIL"
INIT_AGENT = "INIT_AGENT"

INIT_STATE_DATA = {
    "state": {
        "metadata":{
            "current_state": INIT_AGENT,
            "state_update_queue": [],
            "unread_email_threads": [],
            "unread_relevant_email_threads": [],
            "relevant_email_threads": [],
            "timebombs": {},
            "birth_datetime": ""
        },
        "state_data": {}
    }
}

# Agent status
INIT = "INIT"
COMPLETE = "COMPLETE"