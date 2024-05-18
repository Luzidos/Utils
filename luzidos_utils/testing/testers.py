import json
import sys
import unittest
from unittest.mock import patch
import copy
from luzidos_utils.testing.mock.s3 import MockS3
import os
from luzidos_utils.aws_io.s3 import read
from luzidos_utils.aws_io.s3 import write

class BaseTest(unittest.TestCase):
    def __init__(self, test_configs_dir):
        self.test_configs_dir = test_configs_dir
    
    """
    ******************************************************************
                        Overwrite Functions
    ******************************************************************
    """
    def setup(self):
        raise NotImplementedError
    
    def run_test_case(self, function_to_test, payload, mock_data, expected_data):
        raise NotImplementedError
    

    """
    ******************************************************************
                        Util Functions
    ******************************************************************
    """

    def run_test_cases(self, function_to_test):
        for test_config_path in self.load_test_config_paths():
            test_name = test_config_path[len(self.test_configs_dir):]
            payload, mock_data, expected_data = self.load_test_data(test_config_path)
            with self.subTest(test_name):
                self.run_test_case(function_to_test, payload, mock_data, expected_data)
            

    

    def load_test_config_paths(self):
        """
            Load all .py files in the test_configs_dir. Load files from subdirectories as well.
        """
        test_config_paths = []
        for root, dirs, files in os.walk(self.test_configs_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    test_config_paths.append(os.path.join(root, file))
        return test_config_paths
        
    def load_test_data(self, test_config_path):
        with open(test_config_path) as f:
            test_data = json.load(f)
        
        payload = test_data["payload"]
        mock_data = test_data["mock_data"]
        expected_data = test_data["expected_data"]

    """
    ******************************************************************
                        Mock Functions
    ******************************************************************
    """
    
    def patch_s3_read(self, mock_s3: MockS3):
        return patch.multiple(
            'luzidos_utils.aws_io.s3.read',
            read_file_from_s3=self.mock_s3.mock_read_file_from_s3,
            read_dir_filenames_from_s3=self.mock_s3.mock_read_dir_filenames_from_s3,
            list_childdirectories=self.mock_s3.mock_list_childdirectories
        )
    
    def patch_s3_write(self, mock_s3: MockS3):
        return patch.multiple(
            'luzidos_utils.aws_io.s3.write',
            upload_file_to_s3=self.mock_s3.mock_upload_file_to_s3,
            upload_fileobj_to_s3=self.mock_s3.mock_upload_fileobj_to_s3,
            upload_dict_as_json_to_s3=self.mock_s3.mock_upload_dict_as_json_to_s3,
            copy_file=self.mock_s3.mock_copy_file
        )



class ModuleTest(BaseTest):
    def __init__(self, test_config_path):
        super().__init__(test_config_path)
    
    def setup(self):
        self.mock_s3 = None
        self.user_id = None
        self.invoice_id = None
        self.state_data = None
        self.expected_state = None
        self.module_name = None

    def run_test_case(self, function_to_test, payload, mock_data, expected_data):
        self.user_id = payload["user_id"]
        self.invoice_id = payload["invoice_id"]
        self.state_data = payload["state_data"]
        self.expected_state = expected_data["expected_state"]

        self.mock_s3 = MockS3(mock_data["mock_s3_data"])
        self.expected_mock_s3 = MockS3(expected_data["expected_s3_data"])

        with self.patch_s3_read(self.mock_s3), \
            self.patch_s3_write(self.mock_s3):
            self.state_data = function_to_test(self.user_id, self.invoice_id, self.state_data)
        
        self.assert_state_data()

    """
    ******************************************************************
        Assertion Functions
    ******************************************************************
    """

    def assert_state_data(self):
        msg = f"State data does not match expected data after running {self.module_name}"
        self.assertDictEqual(self.state_data, self.expected_state, msg=msg)
    
    def assert_transaction_data(self):
        msg = f"Transaction data does not match expected data after running {self.module_name}"
        with self.patch_s3_read(self.mock_s3):
            transaction_data = read.read_transaction_data_from_s3(self.user_id, self.invoice_id)
        with self.patch_s3_read(self.expected_mock_s3):
            expected_transaction_data = read.read_transaction_data_from_s3(self.user_id, self.invoice_id)
        self.assertDictEqual(transaction_data, expected_transaction_data, msg=msg)

    def assert_user_data(self):
        msg = f"User data does not match expected data after running {self.module_name}"
        with self.patch_s3_read(self.mock_s3):
            user_data = read.read_user_data_from_s3(self.user_id)
        with self.patch_s3_read(self.expected_mock_s3):
            expected_user_data = read.read_user_data_from_s3(self.user_id)
        self.assertDictEqual(user_data, expected_user_data, msg=msg)
    
    def assert_s3_data(self):
        msg = f"Luzidosdatadump data does not match expected data after running {self.module_name}"

        self.assertDictEqual(self.mock_s3.mock_s3_data, self.expected_mock_s3.mock_s3_data, msg=msg)