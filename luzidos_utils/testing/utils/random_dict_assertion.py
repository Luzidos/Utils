import re
from unittest import TestCase

class TestWithRandom(TestCase):
    RANDOM = "<!***RANDOM***!>"

    def assertDictWithRandom(self, actual, expected):
        # Recursively populate the expected dictionary with actual values
        self.populate_expected_with_actual(expected, actual)
        # Use assertDictEqual from unittest.TestCase to compare
        self.assertDictEqual(actual, expected)

    def populate_expected_with_actual(self, expected, actual):
        assert isinstance(expected, dict) and isinstance(actual, dict), "Both expected and actual should be dictionaries."
        
        for key, exp_value in list(expected.items()):
            # Check if the key has a random pattern
            if self.RANDOM in key:
                matched_key = self.match_pattern_key(actual, key)
                assert matched_key, f"No matching keys found for pattern: {key}"
                # Update the key in expected dict
                expected[matched_key] = expected.pop(key)
                key = matched_key
            
            if isinstance(exp_value, dict):
                # Recursive call for nested dictionaries
                self.populate_expected_with_actual(expected[key], actual[key])
            elif self.RANDOM in exp_value:
                # Generate pattern for the value
                pattern = re.compile(exp_value.replace(self.RANDOM, r"\d+"))
                # Match and update the expected value with actual value
                for act_key, act_value in actual.items():
                    if pattern.fullmatch(act_value):
                        expected[key] = act_value
                        break
                assert pattern.fullmatch(actual[key]), f"Value for key '{key}' did not match. Expected pattern: {exp_value}, but was: {actual[key]}"
            else:
                # For non-random, non-dict values, direct comparison
                expected[key] = actual[key]

    def match_pattern_key(self, actual, pattern_key):
        # Create a regex pattern from the key
        pattern = re.compile(pattern_key.replace(self.RANDOM, r"\d+"))
        # Match against all actual keys
        for act_key in actual.keys():
            if pattern.fullmatch(act_key):
                return act_key
        return None

# Example usage
expected_dict = {
    'thread<!***RANDOM***!>id': {
        'email': 'example@example.com',
        'id': 'random.<!***RANDOM***!>@luzidos.com'
    },
    'level1': {
        'level2': {
            'data<!***RANDOM***!>': 'value123'
        }
    }
}

actual_dict = {
    'thread21834id': {
        'email': 'example@example.com',
        'id': 'random.13414541541@luzidos.com'
    },
    'level1': {
        'level2': {
            'data456': 'value123'
        }
    }
}

test = TestWithRandom()
test.assertDictWithRandom(actual_dict, expected_dict)
