import boto3
import json
import datetime as dt
from luzidos_utils.constants import DATE_TIME_FORMAT
from luzidos_utils.timebomb.timebomb_status import ACTIVE, CANCELLED, TRIGGERED
import uuid
def dispatch_timebomb(execution_datetime, state_update):
    """
    Dispatches time bomb to be triggered at a later time
    """
    # Use the EventBridge client to put a scheduled event
    eventbridge = boto3.client('events')
    timebomb_id =  str(uuid.uuid4())
    rule_name = f"trigger-lambda-{timebomb_id}"
    response = eventbridge.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron({execution_datetime.minute} {execution_datetime.hour} {execution_datetime.day} {execution_datetime.month} ? {execution_datetime.year})",
        State='ENABLED',
    )
    

    # Add target to the rule
    target_response = eventbridge.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': timebomb_id,
                'Arn': 'arn:aws:lambda:us-west-2:385772193343:function:timebomb',
                'Input': json.dumps(state_update)
            },
        ]
    )

    return timebomb_id


def cancel_timebomb(timebomb_id):
    """
    Cancels time bomb
    """
    client = boto3.client('events')
    rule_name = f"trigger-lambda-{timebomb_id}"
    client.remove_targets(
        Rule=rule_name,
        Ids=[timebomb_id] 
    )
    client.delete_rule(
        Name=rule_name
    )

def clear_timebombs(thread_id, state_data):
    """
    Clears all timebombs associated with a thread
    """
    for i, timebomb in enumerate(state_data["metadata"]["timebombs"][thread_id]):
        if timebomb["status"] == ACTIVE:
            cancel_timebomb(timebomb["timebomb_id"])
            state_data["metadata"]["timebombs"][thread_id][i]["status"] = CANCELLED
    return state_data


def set_countdown_timebomb(state_update, send_time=None, n_hours=24, n_days=0, n_weeks=0, n_months=0, n_years=0, type= None):
    """
    Sets countdown time bomb
    Send time is the time when the time bomb should be triggered, within the next n_hours, n_days, n_weeks, n_months, or n_years
    """
    current_datetime = dt.datetime.now()
    # Calculate trigger_time based on send_time and n_hours, n_days, n_weeks, n_months, or n_years
    # Trigger_time is the latest posible send_time such that the timebomb is sent within the next n_hours+n_days+n_weeks+n_months+n_years
    trigger_datetime = current_datetime+ dt.timedelta(hours=n_hours, days=n_days, weeks=n_weeks, months=n_months, years=n_years)
    # if send_time is provided, use it to calculate trigger_time
    if send_time:
        # Ex: if currently it is 1pm and send_time is 7am and n_hours is 24, trigger_time is 7am the next day
        # Ex: if currently it is 5 am and send_time is 7am and n_hours is 24, trigger_time is 7am the same day
        if trigger_datetime.time() >= send_time.time():
            trigger_datetime = dt.datetime.combine(trigger_datetime.date(), send_time.time())
        else:
            trigger_datetime = dt.datetime.combine(current_datetime.date(), send_time.time())
    timebomb_id = dispatch_timebomb(trigger_datetime, state_update)
    if type == None:
        type = f"COUNTDOWN@{send_time}-{n_hours}H-{n_days}D-{n_weeks}W-{n_months}M-{n_years}Y"
    return {
            'timebomb_id': timebomb_id, 
            'status': ACTIVE, 
            'set_datetime': current_datetime.strftime(DATE_TIME_FORMAT),
            'trigger_datetime': trigger_datetime.strftime(DATE_TIME_FORMAT),
            'type': type
            }

def set_end_of_month_timebomb(state_update, send_time=None, n_days=3, business_days=True):
    """
    Sets end of month time bomb
    """
    raise NotImplementedError

    trigger_time = None

    return dispatch_timebomb(trigger_time, state_update)