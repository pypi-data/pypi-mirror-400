# pip install pycryptodome==3.10.1
# pip install esdk-obs-python
# 引入模块
import os

from obs import ObsClient, GetObjectHeader


class BaseObsClient(object):

    def __init__(self, aws_access_key_id="", aws_secret_access_key="", endpoint_url=""):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.client = None
        if self.aws_access_key_id and self.aws_secret_access_key and self.endpoint_url:
            self.get_client()

    def get_client(self):
        self.client = ObsClient(access_key_id=self.aws_access_key_id,
                                secret_access_key=self.aws_secret_access_key,
                                server=self.endpoint_url)
        return self

    def close(self):
        self.client.close()

    def put_object(self, bucket_name, objectKey, body):
        """
        直接写内容到文件
        Args:
            bucket_name:
            key:
            body: 需要

        Returns:
        """
        # 上传文本对象
        resp = self.client.putContent(bucket_name, objectKey, body)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True, resp
        else:
            return False, resp


    def download_memobj(self, bucket_name, objectKey):
        """
        return: None
        """
        # 指定loadStreamInMemory为True忽略downloadpath路径，将文件的二进制流下载到内存
        # 二进制下载对象
        resp = self.client.getObject(bucketName=bucket_name, objectKey=objectKey, loadStreamInMemory=True)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True, resp
        else:
            return False, resp

    def download_file(self, bucket_name, objectKey,downloadPath):
        """
        return: None
        """
        headers = GetObjectHeader()
        resp = self.client.getObject(bucket_name, objectKey, downloadPath, headers=headers)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True, resp
        else:
            return False, resp


    def list_prefixes(self,bucket_name,prefix, max_keys = 100):
        # 列举桶内对象
        resp = self.client.listObjects(bucket_name, prefix, max_keys=max_keys, encoding_type='url')
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            return True, resp
        else:
            return False, resp