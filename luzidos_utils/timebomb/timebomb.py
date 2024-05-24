import boto3
import json
import datetime as dt
from luzidos_utils.constants.format import DATE_TIME_FORMAT
from luzidos_utils.timebomb.timebomb_status import ACTIVE, CANCELLED, TRIGGERED
import uuid
from dateutil.relativedelta import relativedelta
import pytz
from luzidos_utils.constants.aws import REGION_NAME
def dispatch_timebomb(execution_datetime, timebomb_payload ):
    """
    Dispatches time bomb to be triggered at a later time
    """
    # Use the EventBridge client to put a scheduled event
    client = boto3.client('events', region_name=REGION_NAME)
    timebomb_id =  str(uuid.uuid4())
    timebomb_payload["metadata"]["timebomb_id"] = timebomb_id
    rule_name = f"trigger-lambda-{timebomb_id}"
    response = client.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron({execution_datetime.minute} {execution_datetime.hour} {execution_datetime.day} {execution_datetime.month} ? {execution_datetime.year})",
        State='ENABLED',
    )

    

    # Add target to the rule
    target_response = client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': timebomb_id,
                'Arn': 'arn:aws:lambda:us-west-2:385772193343:function:timebomb',
                'Input': json.dumps(timebomb_payload)
            },
        ]
    )

    return timebomb_payload["metadata"]


def cancel_timebomb(timebomb_id):
    """
    Cancels time bomb
    """
    client = boto3.client('events', region_name=REGION_NAME)
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
    for timebomb_id in state_data["state"]["metadata"]["timebombs"][thread_id]:
        timebomb = state_data["state"]["metadata"]["timebombs"][thread_id][timebomb_id]
        if timebomb["status"] == ACTIVE:
            cancel_timebomb(timebomb["timebomb_id"])
            state_data["state"]["metadata"]["timebombs"][thread_id][timebomb_id]["status"] = CANCELLED
    return state_data

def round_up_to_time(utc_datetime, time_tuple):
    # Unpack the time tuple
    target_hour, target_minute, target_tz_name = time_tuple
    
    # Load the timezone object
    target_tz = pytz.timezone(target_tz_name)
    
    # Convert the UTC datetime object to the target timezone
    local_datetime = utc_datetime.astimezone(target_tz)
    
    # Create a new datetime object for the target time on the same day
    target_datetime = local_datetime.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # If the target datetime is in the past, move to the next day
    if target_datetime < local_datetime:
        target_datetime += dt.timedelta(days=1)
    
    # Return the result in UTC
    return target_datetime.astimezone(pytz.utc)

def set_countdown_timebomb(timebomb_payload, send_time=None, n_hours=24, n_days=0, n_weeks=0, n_months=0, n_years=0, type= None):
    """
    Sets countdown time bomb
    Send time is the time when the time bomb should be triggered, within the next n_hours, n_days, n_weeks, n_months, or n_years
    """
    current_datetime = dt.datetime.now()
    # Calculate trigger_time based on send_time and n_hours, n_days, n_weeks, n_months, or n_years
    # Trigger_time is the latest posible send_time such that the timebomb is sent within the next n_hours+n_days+n_weeks+n_months+n_years
    trigger_datetime = current_datetime+ relativedelta(hours=n_hours, days=n_days, weeks=n_weeks, months=n_months, years=n_years)
    # if send_time is provided, use it to calculate trigger_time
    if send_time:
        # round_up_to_time(trigger_datetime, (12, 10, "America/Bogota"))
        trigger_datetime = round_up_to_time(trigger_datetime, send_time)

    if type == None:
        type = f"COUNTDOWN@{send_time}-{n_hours}H-{n_days}D-{n_weeks}W-{n_months}M-{n_years}Y"

    timebomb_payload["metadata"]["status"] = ACTIVE
    timebomb_payload["metadata"]["set_datetime"] = current_datetime.strftime(DATE_TIME_FORMAT)
    timebomb_payload["metadata"]["trigger_datetime"] = trigger_datetime.strftime(DATE_TIME_FORMAT)
    timebomb_payload["metadata"]["type"] = type
    timebomb_payload["metadata"]["timebomb_id"] = None

    timebomb_metadata = dispatch_timebomb(trigger_datetime, timebomb_payload)

    return timebomb_metadata

def set_end_of_month_timebomb(state_update, send_time=None, n_days=3, business_days=True):
    """
    Sets end of month time bomb
    """
    raise NotImplementedError

    trigger_time = None

    return dispatch_timebomb(trigger_time, state_update)