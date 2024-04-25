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
    timebomb_update = {}
    timebomb_update["user_id"] = user_id
    timebomb_update["invoice_id"] = invoice_id
    timebomb_update["state_update"] = {
        "state": SEND_EMAIL, 
        "state_data": {
            "focused_email_thread_id": thread_id,
            "email_response_type": response_type
        }
    }
    if context is not None:
        timebomb_update["state_update"]["state_data"]["context"] = context


    timebomb_metadata = timebomb.set_countdown_timebomb(
        timebomb_update,
        send_time = (8,0, 'America/Bogota'),
        n_hours=24,
        type="1d_followup"
    )
    

    state_data["state"]["metadata"]["timebombs"][thread_id].append(timebomb_metadata)
    return state_data