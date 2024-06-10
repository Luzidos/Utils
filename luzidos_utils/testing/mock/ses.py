import json
from datetime import datetime

class MockSES:
    def __init__(self, workmail_data=None):
        if 'messages' not in workmail_data:
            workmail_data['messages'] = {}
        self.workmail_data = workmail_data

    def send_raw_email(self, Source, Destinations, RawMessage):
        email_record = {
            'Source': Source,
            'Destinations': Destinations,
            'RawMessage': RawMessage,
            'Timestamp': datetime.now().isoformat()
        }
        message_id = str(hash(json.dumps(email_record)))  # Simulated Message ID
        self.workmail_data['messages'][message_id] = RawMessage  # Store message content in shared messages
        return {'MessageId': message_id}
