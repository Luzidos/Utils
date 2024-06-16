import os
import json
import boto3
import luzidos_utils.aws_io.s3.read as s3_read
import luzidos_utils.aws_io.s3.write as s3_write

class MockS3:
    def __init__(self, mock_s3_data: dict):
        # pop "_override_paths" from mock_s3_data
        self.override_paths = mock_s3_data.pop("_override_paths", [])
        self.mock_s3_data = mock_s3_data

        self.patchers = []

    def set_patchers(self, patchers):
        self.patchers = patchers

    """
    ******************************************************************
                    luzidos_utils.aws_io.s3.read Mock Functions
    ******************************************************************
    """

    def mock_read_file_from_s3(self, bucket_name, object_name):
        """
        Mock function for read_file_from_s3
        This function reads from self.mock_s3_data dictionary.
        The bucket_name and object_name are used as keys for nested dictionaries.
        Each "/" in the object_name is used to traverse the nested dictionaries.
        """
        if f"{bucket_name}/{object_name}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
            res = s3_read.read_file_from_s3(bucket_name, object_name)
            for patcher in self.patchers:
                patcher.start()
            return res
        
        try:
            data = self.mock_s3_data[bucket_name]
            for key in object_name.split("/"):
                data = data[key]

            if isinstance(data, dict):
                return json.dumps(data)
            
            
            # If file is a valid file path, then read the file
            if os.path.isfile(str(data)):
                with open(str(data), "r") as f:
                    data = f.read()
                    return data
        except Exception as e:
            print(e, f"\nMock file not found in {bucket_name}/{object_name}")
            return None
        
        return data

    def mock_read_dir_filenames_from_s3(self, bucket_name, dir_name):
        """
        Mock function for read_dir_filenames_from_s3
        This function reads from self.mock_s3_data dictionary.
        The bucket_name and dir_name are used as keys for nested dictionaries.
        Each "/" in the dir_name is used to traverse the nested dictionaries.
        The original function returns a list of all the filenames in the directory.
        This includes files inside subdirectories.
        This function returns the full path to each file object.
        """
        if f"{bucket_name}/{dir_name}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
                res = s3_read.read_dir_filenames_from_s3(bucket_name, dir_name)
            for patcher in self.patchers:
                patcher.start()
            return res
        
        current_level = self.mock_s3_data.get(bucket_name, {})
        path_parts = dir_name.strip('/').split('/')

        for part in path_parts:
            current_level = current_level.get(part, {})
        
        filenames = []

        def traverse(level, path):
            # if . is in the path, then it should be treated as a file
            # otherwise it should be treated as a directory
            for key, value in level.items():
                if '.' in key:
                    filenames.append(f"{path}/{key}")
                else:
                    traverse(value, f"{path}/{key}")

        traverse(current_level, dir_name.strip('/'))
        return filenames
        
        

    def mock_list_childdirectories(self, bucket_name, prefix):
        """
        Mock function for list_childdirectories

        This function reads from self.mock_s3_data dictionary.
        The bucket_name and prefix are used as keys for nested dictionaries.
        Each "/" in the prefix is used to traverse the nested dictionaries.
        This function returns a list of all the directories at the specified prefix.
        The directories are returned as full paths.
        The directories should be immediate children.
        """
        if f"{bucket_name}/{prefix}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
                res = s3_read.list_childdirectories(bucket_name, prefix)
            for patcher in self.patchers:
                patcher.start()
            return res
        
        current_level = self.mock_s3_data.get(bucket_name, {})
        path_parts = prefix.strip('/').split('/')

        for part in path_parts:
            current_level = current_level.get(part, {})
        
        subfolders = []
        
        for key, value in current_level.items():
            if isinstance(value, dict):
                subfolders.append(f"{prefix.strip('/')}/{key}/")

        return subfolders

    """
    ******************************************************************
                    luzidos_utils.aws_io.s3.write Mock Functions
    ******************************************************************
    """
    
    def mock_upload_file_to_s3(self, file_path, bucket_name, object_name):
        """
        Mock function for upload_file_to_s3
        This function writes to self.mock_s3_data dictionary.
        The bucket_name and dir_name are used as keys for nested dictionaries.
        Each "/" in the dir_name is used to traverse the nested dictionaries.

        We set file_path as the value of the last key in the nested dictionaries.
        """
        if f"{bucket_name}/{object_name}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
                res = s3_write.upload_file_to_s3(file_path, bucket_name, object_name)
            for patcher in self.patchers:
                patcher.start()
            return res
        
        current_level = self.mock_s3_data.setdefault(bucket_name, {})
        path_parts = object_name.strip('/').split('/')

        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})

        current_level[path_parts[-1]] = file_path
        return True

    
    def mock_upload_file_obj_to_s3(self, file_obj, bucket_name,  object_name):
        """
        Mock function for upload_file_obj_to_s3
        """
        if f"{bucket_name}/{object_name}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
                res = s3_write.upload_file_obj_to_s3(file_obj, bucket_name, object_name)
            for patcher in self.patchers:
                patcher.start()
            return res
        
        current_level = self.mock_s3_data.setdefault(bucket_name, {})
        path_parts = object_name.strip('/').split('/')

        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})

        current_level[path_parts[-1]] = file_obj
        return True
        
    
    def mock_upload_dict_as_json_to_s3(self, bucket_name, dict_data, object_name):
        """
        Mock function for upload_dict_as_json_to_s3
        """
        if f"{bucket_name}/{object_name}" in self.override_paths:
            for patcher in self.patchers:
                patcher.stop()
                res = s3_write.upload_dict_as_json_to_s3(bucket_name, dict_data, object_name)
            for patcher in self.patchers:
                patcher.start()
            return res
        current_level = self.mock_s3_data.setdefault(bucket_name, {})
        path_parts = object_name.strip('/').split('/')

        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})

        current_level[path_parts[-1]] = dict_data
        return True
    
    def mock_copy_file(self, bucket_name, source_file, dest_file):
        """
        Mock function for copy_file
        
        """
        source_content = self.mock_read_file_from_s3(bucket_name, source_file)
        self.mock_upload_file_obj_to_s3(source_content, bucket_name, dest_file)
        # if f"{bucket_name}/{dest_file}" in self.override_paths:
        #     for patcher in self.patchers:
        #         patcher.stop()
        #         res = s3_write.upload_file
        #     for patcher in self.patchers:
        #         patcher.start()
        #     return res
        # data = self.mock_s3_data[bucket_name]
        # for key in source_file.split("/"):
        #     data = data[key]

        # source_content = data

        # current_level = self.mock_s3_data.setdefault(bucket_name, {})
        # path_parts = dest_file.strip('/').split('/')

        # for part in path_parts[:-1]:
        #     current_level = current_level.setdefault(part, {})
    
        # current_level[path_parts[-1]] = source_content
        return True

# class MockS3:
#     def __init__(self, data=None):
#         # data is a dictionary where each key is a bucket name
#         # and its value is another dictionary, where each key is an object key and its value is the object content
#         if data is None:
#             data = {}
#         self.override_paths = data.pop("_override_paths", [])
#         self.data = data

#     def get_object(self, Bucket, Key):
#         if f"{Bucket}/{Key}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             return s3_client.get_object(Bucket=Bucket, Key=Key)
#         try:
#             bucket_data = self.data.get(Bucket, {})
#             if Key in bucket_data:
#                 return {'Body': bucket_data[Key]}
#             else:
#                 raise Exception(f"Object {Key} not found in bucket {Bucket}")
#         except Exception as e:
#             return {'Error': str(e)}

#     def list_objects_v2(self, Bucket, Prefix=''):
#         if f"{Bucket}/{Prefix}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             return s3_client.list_objects_v2(Bucket=Bucket, Prefix=Prefix)
#         try:
#             bucket_data = self.data.get(Bucket, {})
#             objects = [{'Key': key} for key in bucket_data if key.startswith(Prefix)]
#             return {'Contents': objects}
#         except KeyError:
#             return {'Error': f"No bucket named {Bucket}"}

#     def copy_object(self, Bucket, CopySource, Key):
#         source_bucket, source_key = CopySource['Bucket'], CopySource['Key']
#         if f"{Bucket}/{Key}" in self.override_paths or f"{source_bucket}/{source_key}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             return s3_client.copy_object(Bucket=Bucket, CopySource=CopySource, Key=Key)
#         try:
#             self.data[Bucket][Key] = self.data[source_bucket][source_key]
#             return {'CopyObjectResult': {'ETag': '"copied"', 'LastModified': 'DateTime'}}
#         except KeyError:
#             return {'Error': f"Failed to copy from {source_key} in {source_bucket} to {Key} in {Bucket}"}

#     def upload_file(self, Filename, Bucket, Key):
#         if f"{Bucket}/{Key}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             s3_client.upload_file(Filename, Bucket, Key)
#             return {'UploadFileResult': 'Success'}
#         try:
#             with open(Filename, 'rb') as f:
#                 self.data.setdefault(Bucket, {})[Key] = f.read()
#             return {'UploadFileResult': 'Success'}
#         except Exception as e:
#             return {'Error': str(e)}

#     def put_object(self, Bucket, Key, Body):
#         if f"{Bucket}/{Key}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             return s3_client.put_object(Bucket=Bucket, Key=Key, Body=Body)
#         try:
#             self.data.setdefault(Bucket, {})[Key] = Body
#             return {'PutObjectResult': 'Success'}
#         except Exception as e:
#             return {'Error': str(e)}

#     def upload_fileobj(self, Fileobj, Bucket, Key):
#         if f"{Bucket}/{Key}" in self.override_paths:
#             s3_client = boto3.client('s3', region_name='us-west-2')
#             s3_client.upload_fileobj(Fileobj, Bucket, Key)
#             return {'UploadFileObjResult': 'Success'}
#         try:
#             Fileobj.seek(0)
#             self.data.setdefault(Bucket, {})[Key] = Fileobj.read()
#             return {'UploadFileObjResult': 'Success'}
#         except Exception as e:
#             return {'Error': str(e)}
