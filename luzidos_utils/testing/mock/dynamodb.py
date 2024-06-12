class MockTable:
    def __init__(self, table_name, data_store):
        self.table_name = table_name
        self.data_store = data_store.get(table_name, {})

    def get_item(self, Key):
        key_name, key_value = next(iter(Key.items()))
        item = self.data_store.get(key_value)
        if item:
            return {
                'Item': {
                    "value": item
                }
            }
        else:
            return {'Error': f"No item found with {key_name}: {key_value}"}

class MockDynamoDB:
    def __init__(self, mock_dynamodb_data=None):
        if mock_dynamodb_data is None:
            mock_dynamodb_data = {}
        self.mock_dynamodb_data = mock_dynamodb_data

    def Table(self, table_name):
        return MockTable(table_name, self.mock_dynamodb_data)
