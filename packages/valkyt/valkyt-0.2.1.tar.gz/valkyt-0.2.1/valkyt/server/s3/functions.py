import os
import json

from json import dumps

from typing import Any
from botocore.exceptions import ClientError
from .connection import ConnectionS3

from valkyt.utils import Stream, File

class S3(ConnectionS3):
    def __init__(self, bucket, service_name, aws_access_key_id, aws_secret_access_key, endpoint_url, **kwargs):
        super().__init__(bucket, service_name, aws_access_key_id, aws_secret_access_key, endpoint_url, **kwargs)
        
    def read_json(self, key: str) -> Any:
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                empty_json = {}
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=json.dumps(empty_json, indent=2, ensure_ascii=False)
                )
                return empty_json
            else:
                raise 

    def upload_json(self, destination: str, body: dict, send: bool = True) -> int:
        if send: 
            response: dict = self.client.put_object(
                Bucket=self.bucket, 
                Key=destination, 
                Body=dumps(body, indent=2, ensure_ascii=False)
                )
            Stream.s3(destination, response['ResponseMetadata']['HTTPStatusCode'])
            return response['ResponseMetadata']['HTTPStatusCode']
        ...
        
    def upload_file(self, path: str, destination: str, send: bool = True) -> int:
        if send: 
            response: dict = self.client.put_object(
                                Bucket=self.bucket,
                                Key = destination, 
                                Body = open(path, 'rb')
                            )
            Stream.s3(destination, response['ResponseMetadata']['HTTPStatusCode'])
            return response['ResponseMetadata']['HTTPStatusCode']
        ...
        
    def upload(self, body: any, destination: str, send: bool = True) -> int:
        if send: 
            response: dict = self.client.put_object(
                                Bucket=self.bucket,
                                Key = destination, 
                                Body = body
                            )
            Stream.s3(destination, response['ResponseMetadata']['HTTPStatusCode'])
            return response['ResponseMetadata']['HTTPStatusCode']
        ...
        
    def local2s3(self, source: str) -> None:
        for root, dirs, files in os.walk(source.replace('\\', '/')):
            for file in files:
                file_path = os.path.join(root, file).replace('\\', '/')
                
                if 'json' in file_path:
                    _temp: dict = File.read_json(file_path)
                    _temp["path_data_raw"] = list(
                        map(
                            lambda x: x.replace('//', '/'),
                            _temp["path_data_raw"]
                        )
                    )
                    
                    File.write_json(
                        file_path,
                        _temp
                    )
                
                Stream.share(file_path)

                S3.upload_file(
                    path=file_path,
                    destination=file_path,
                )
