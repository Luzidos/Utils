

class MockS3:
    def __init__(self, mock_s3_data):
        self.mock_s3_data = mock_s3_data

    """
    ******************************************************************
                    luzidos_utils.aws_io.s3.read Mock Functions
    ******************************************************************
    """

    def mock_read_file_from_s3(self, bucket_name, object_name):
        """
        Mock function for read_file_from_s3
        """
        return None

    def mock_read_dir_filenames_from_s3(self, bucket_name, dir_name):
        """
        Mock function for read_dir_filenames_from_s3
        """
        return None

    def mock_list_childdirectories(self, bucket_name, prefix):
        """
        Mock function for list_childdirectories
        """
        return None

    """
    ******************************************************************
                    luzidos_utils.aws_io.s3.write Mock Functions
    ******************************************************************
    """
    
    def mock_upload_file_to_s3(self, bucket_name, object_name, file_path):
        """
        Mock function for upload_file_to_s3
        """
        return None
    
    def mock_upload_fileobj_to_s3(self, bucket_name, object_name, fileobj):
        """
        Mock function for upload_fileobj_to_s3
        """
        return None
    
    def mock_upload_dict_as_json_to_s3(self, bucket_name, object_name, data):
        """
        Mock function for upload_dict_as_json_to_s3
        """
        return None
    
    def mock_copy_file(bucket_name, source_file, dest_file):
        """
        Mock function for copy_file
        """
        return None