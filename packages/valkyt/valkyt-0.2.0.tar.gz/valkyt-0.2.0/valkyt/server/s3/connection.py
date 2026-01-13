import boto3

class ConnectionS3:
    def __init__(
        self, 
        bucket: str, 
        service_name: str, 
        aws_access_key_id: str, 
        aws_secret_access_key: str, 
        endpoint_url: str, 
        **kwargs
    ) -> None:
        self.bucket = bucket

        self.client = boto3.client(
            service_name=service_name,
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key, 
            endpoint_url=endpoint_url
        )
