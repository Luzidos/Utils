import json
import sys
import unittest
from unittest.mock import patch
import copy
from luzidos_utils.testing.mock.s3 import MockS3
from luzidos_utils.testing.mock.boto3 import MockBoto3
import os
from luzidos_utils.aws_io.s3 import read
from luzidos_utils.aws_io.s3 import write
import runpy
import tempfile


def load_test_config_paths(test_configs_dir):
    """
        Load all .py files in the test_configs_dir. Load files from subdirectories as well.
    """
    test_config_paths = []
    for root, dirs, files in os.walk(test_configs_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("."):
                test_config_paths.append(os.path.join(root, file))
    return test_config_paths

def create_module_test_cases(function_to_test, test_configs_dir):
    test_config_paths = load_test_config_paths(test_configs_dir)
    test_instances = []
    for test_config_path in sorted(test_config_paths):
        test_instances.append(ModuleTest(function_to_test, test_config_path))
    return test_instances

def run_file_contents(file_contents = None, file_path = None):
    del_file= False

    if file_path is None:
        del_file = True
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            file_path = temp_file.name
            temp_file.write(file_contents.encode('utf-8'))
    
    try:
        # Use runpy to execute the temporary file in a separate namespace
        result = runpy.run_path(file_path)
    finally:
        if del_file:
            # Ensure the temporary file is deleted after execution
            os.remove(file_path)
    
    return result

class BaseTest(unittest.TestCase):
    def __init__(self, function_to_test, test_config_path):
        super().__init__("run_test_case")
        self.function_to_test = function_to_test
        self.test_config_path = test_config_path
        self.payload = None
        self.mock_data = None
        self.expected_data = None
        self.maxDiff = None
        self.load_test_data(self.test_config_path)
    
    """
    ******************************************************************
                        Overwrite Functions
    ******************************************************************
    """
    def setup(self):
        raise NotImplementedError
    
    def run_test_case(self):
        raise NotImplementedError
    
    def __str__(self):
        raise NotImplementedError
    

    """
    ******************************************************************
                        Util Functions
    ******************************************************************
    """


    def load_test_data(self, test_config_path):
        # with open(test_config_path, 'r') as file:
        #     file_contents = file.read()
        # test_configs = {}
        # exec(file_contents, {}, test_configs)
        test_configs = run_file_contents(file_path=test_config_path)
        test_data = test_configs.get('test_configs')
        
        self.payload = test_data["payload"]
        self.mock_data = test_data["mock_data"]
        self.expected_data = test_data["expected_data"]
        


    """
    ******************************************************************
                        Mock Functions
    ******************************************************************
    """
    
    def patch_s3_read(self, mock_s3: MockS3):
        return patch.multiple(
            'luzidos_utils.aws_io.s3.read',
            read_file_from_s3=mock_s3.mock_read_file_from_s3,
            read_dir_filenames_from_s3=mock_s3.mock_read_dir_filenames_from_s3,
            list_childdirectories=mock_s3.mock_list_childdirectories
        )
    
    def patch_s3_write(self, mock_s3: MockS3):
        return patch.multiple(
            'luzidos_utils.aws_io.s3.write',
            upload_file_to_s3=mock_s3.mock_upload_file_to_s3,
            upload_file_obj_to_s3=mock_s3.mock_upload_file_obj_to_s3,
            upload_dict_as_json_to_s3=mock_s3.mock_upload_dict_as_json_to_s3,
            copy_file=mock_s3.mock_copy_file
        )
    
    def patch_boto3_client(self, mock_boto3):
        return patch(
            'boto3.client', 
           new=mock_boto3.mock_client 
        )

    def patch_boto3_resource(self, mock_boto3):
        return patch(
            'boto3.resource', 
           new=mock_boto3.mock_resource 
        )


class ModuleTest(BaseTest):
    def __init__(self, function_to_test, test_config_dir):
        super().__init__(function_to_test, test_config_dir)
        self.module_name = self.function_to_test.__name__
    
    def setup(self):
        pass

    def run_test_case(self):
        self.user_id = self.payload["user_id"]
        self.invoice_id = self.payload["invoice_id"]
        self.state_data = self.payload["state_data"]
        self.expected_state = self.expected_data["expected_state"]

        self.mock_s3 = MockS3(self.mock_data["mock_s3_data"])
        self.expected_mock_s3 = MockS3(self.expected_data["expected_s3_data"])

        self.mock_boto3 = MockBoto3(self.mock_data["mock_boto3_data"])
        self.expected_boto3 = MockBoto3(self.expected_data["expected_boto3_data"])

        s3_read_patcher = self.patch_s3_read(self.mock_s3)
        s3_write_patcher = self.patch_s3_write(self.mock_s3)

        boto3_client_patcher = self.patch_boto3_client(self.mock_boto3)
        boto3_resource_patcher = self.patch_boto3_resource(self.mock_boto3)

        patchers = [s3_read_patcher, s3_write_patcher, boto3_client_patcher, boto3_resource_patcher]
        self.mock_s3.set_patchers(patchers)

        for patcher in patchers:
            patcher.start()
        self.state_data = self.function_to_test(self.user_id, self.invoice_id, self.state_data)
        for patcher in patchers:
            patcher.stop()

        self.assert_state_data()
        self.assert_transaction_data()
        self.assert_user_data()
        self.assert_email_s3_data()
        self.assert_s3_data()
        self.assert_eventbridge_data()
        self.assert_workmail_data()
        self.assert_boto3_data()


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

    def assert_email_s3_data(self):
        msg = f"Email data does not match expected data after running {self.module_name}"
        mock_email_data = self.mock_s3.mock_s3_data["luzidosdatadump"]["public"][self.user_id]["emails"]
        expected_email_data = self.expected_mock_s3.mock_s3_data["luzidosdatadump"]["public"][self.user_id]["emails"]
        self.assertDictEqual(mock_email_data, expected_email_data, msg=msg)

    def assert_eventbridge_data(self):
        msg = f"Eventbridge data does not match expected data after running {self.module_name}"
        mock_eventbridge_data = None
        expected_eventbridge_data = None
        if "eventbridge_data" in self.mock_boto3.mock_data:
            mock_eventbridge_data = self.mock_boto3.mock_data["eventbridge_data"]
        if "eventbridge_data" in self.expected_boto3.mock_data:
            expected_eventbridge_data = self.expected_boto3.mock_data["eventbridge_data"]
        self.assertDictEqual(mock_eventbridge_data, expected_eventbridge_data, msg=msg)
    
    def assert_workmail_data(self):
        msg = f"Workmail data does not match expected data after running {self.module_name}"
        mock_workmail_data = None
        expected_workmail_data = None
        if "workmail_data" in self.mock_boto3.mock_data:
            mock_workmail_data = self.mock_boto3.mock_data["workmail_data"]
        if "workmail_data" in self.expected_boto3.mock_data:
            expected_workmail_data = self.expected_boto3.mock_data["workmail_data"]
        self.assertDictEqual(mock_workmail_data, expected_workmail_data, msg=msg)

    def assert_boto3_data(self):
        msg = f"Boto3 data does not match expected data after running {self.module_name}"
        self.assertDictEqual(self.mock_boto3.mock_data, self.expected_boto3.mock_data, msg=msg)

    def __str__(self):
        test_name = self.test_config_path.split("configs/")[1]
        return f"ModuleTest: {test_name}"