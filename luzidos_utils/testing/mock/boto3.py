import boto3
from luzidos_utils.testing.mock.eventbridge import MockEventBridge
from luzidos_utils.testing.mock.ses import MockSES
from luzidos_utils.testing.mock.workmailmessageflow import MockWorkMailMessageFlow

class MockBoto3:
    def __init__(self, mock_data=None):
        self.mock_data = mock_data

    def mock_client(self, service_name, **kwargs):
        if service_name == 'events' and 'eventbridge_data' in self.mock_data:
            return MockEventBridge(self.mock_data['eventbridge_data'])
        elif service_name == 'ses' and 'workmail_data' in self.mock_data:
            return MockSES(self.mock_data['workmail_data'])
        elif service_name == 'workmailmessageflow' and 'workmail_data' in self.mock_data:
            return MockWorkMailMessageFlow(self.mock_data['workmail_data'])
        return boto3.client(service_name, **kwargs)

    