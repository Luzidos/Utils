from luzidos_utils.constants.state import (
    GENERIC_FOLLOWUP, SEND_EMAIL
)

from luzidos_utils.timebomb import timebomb

def set_1d_followup_timebomb(user_id, invoice_id, state_data, response_type=GENERIC_FOLLOWUP, thread_id= None, context=None):
    """
    Sets a 1 day followup timebomb to the focused email thread
    """
    if thread_id is None:
        thread_id = state_data["state"]["state_data"]["focused_email_thread_id"]
    timebomb_payload = {"state_update": None, "metadata": None}
    timebomb_payload["metadata"] = {
        "user_id": user_id,
        "invoice_id": invoice_id,
        "thread_id": thread_id,
    }
    timebomb_payload["state_update"] = {
        "state": SEND_EMAIL, 
        "state_data": {
            "focused_email_thread_id": thread_id,
            "email_response_type": response_type
        }
    }
    if context is not None:
        timebomb_payload["state_update"]["state_data"]["context"] = context


    timebomb_metadata = timebomb.set_countdown_timebomb(
        timebomb_payload,
        send_time = (8,0, 'America/Bogota'),
        n_hours=24,
        type="1d_followup"
    )
    
    timebomb_id = timebomb_metadata["timebomb_id"]
    state_data["state"]["metadata"]["timebombs"][thread_id][timebomb_id] = timebomb_metadata
    return state_data

def set_next_day_followup_timebomb(user_id, invoice_id, state_data, response_type=GENERIC_FOLLOWUP, thread_id= None, context=None):
    """
    Sets a 1 day followup timebomb to the focused email thread
    """
    if thread_id is None:
        thread_id = state_data["state"]["state_data"]["focused_email_thread_id"]
    timebomb_payload = {"state_update": None, "metadata": None}
    timebomb_payload["metadata"] = {
        "user_id": user_id,
        "invoice_id": invoice_id,
        "thread_id": thread_id,
    }
    timebomb_payload["state_update"] = {
        "state": SEND_EMAIL, 
        "state_data": {
            "focused_email_thread_id": thread_id,
            "email_response_type": response_type
        }
    }
    if context is not None:
        timebomb_payload["state_update"]["state_data"]["context"] = context


    timebomb_metadata = timebomb.set_countdown_timebomb(
        timebomb_payload,
        send_time = (8,0, 'America/Bogota'),
        n_hours=8,
        type="next_day_followup"
    )
    
    timebomb_id = timebomb_metadata["timebomb_id"]
    state_data["state"]["metadata"]["timebombs"][thread_id][timebomb_id] = timebomb_metadata
    return state_data