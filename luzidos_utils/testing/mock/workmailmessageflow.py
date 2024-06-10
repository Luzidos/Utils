import json
from datetime import datetime

class MockWorkMailMessageFlow:
    def __init__(self, workmail_data):
        if 'messages' not in workmail_data:
            workmail_data['messages'] = {}
        self.workmail_data = workmail_data

    def get_raw_message_content(self, messageId):
        if messageId in self.workmail_data['messages']:
            return {'messageContent': self.workmail_data['messages'][messageId]}
        else:
            raise ValueError("Message ID not found")
