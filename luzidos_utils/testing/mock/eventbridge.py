import json
from datetime import datetime

class MockEventBridge:
    def __init__(self, mock_eventbridge_data=None):
        if mock_eventbridge_data is None:
            mock_eventbridge_data = {'rules': {}, 'targets': {}}
        self.rules = mock_eventbridge_data.get('rules', {})
        self.targets = mock_eventbridge_data.get('targets', {})

    """
    ******************************************************************
                    boto3.client Mock Functions
    ******************************************************************
    """
    def remove_targets(self, Rule, Ids):
        if Rule in self.targets:
            self.targets[Rule] = [target for target in self.targets[Rule] if target['Id'] not in Ids]
            if not self.targets[Rule]:
                del self.targets[Rule]

    def delete_rule(self, Name):
        if Name in self.rules:
            del self.rules[Name]

    def put_rule(self, Name, ScheduleExpression, State):
        self.rules[Name] = {
            'ScheduleExpression': ScheduleExpression,
            'State': State,
            'CreationTime': datetime.now().isoformat()
        }
        return {'RuleArn': f'arn:aws:events:region:account-id:rule/{Name}'}

    def put_targets(self, Rule, Targets):
        if Rule not in self.rules:
            raise ValueError(f"Rule {Rule} does not exist.")
        if Rule not in self.targets:
            self.targets[Rule] = []
        self.targets[Rule].extend(Targets)
        return {'FailedEntryCount': 0, 'FailedEntries': []}
