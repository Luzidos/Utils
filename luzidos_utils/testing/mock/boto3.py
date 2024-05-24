import boto3
from luzidos_utils.testing.mock.eventbridge import MockEventBridge

class MockBoto3:
    def __init__(self, mock_data=None):
        self.mock_data = mock_data

    def mock_client(self, service_name, **kwargs):
        if service_name == 'events':
            return MockEventBridge(self.mock_data['eventbridge_data'])
        return boto3.client(service_name, **kwargs)

    