import gzip
import io
from typing import Protocol

import aioboto3
import aiofiles
from aiobotocore.config import AioConfig


class AsyncReadable(Protocol):
    async def read(self, n: int = -1) -> bytes:
        ...


# config = AioConfig(connect_timeout=600000, read_timeout=600000, retries={'max_attempts': 3},
#                    max_pool_connections=10)

class BaseAioBoto3(object):

    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url,
                 config=AioConfig(max_pool_connections=10)):
        """
          初始化华为云 OBS 客户端

          Args:
              access_key: 华为云 Access Key
              secret_key: 华为云 Secret Key
              region: 区域，如 'cn-north-4'
              endpoint: 华为云 OBS 端点，可选
          """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.config = config
        self.boto_session = None

    async def initialize_class_variable(self):
        if self.boto_session is None:
            self.boto_session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )

    async def read_minio_data(self, bucket, key):
        await self.initialize_class_variable()
        async with self.boto_session.client("s3", endpoint_url=self.endpoint_url, config=self.config) as s3:
            s3_ob = await s3.get_object(Bucket=bucket, Key=key)
            result = await s3_ob["Body"].read()
            return result

    def ungzip(self, raw_bytes, encoding="utf-8"):
        with gzip.GzipFile(fileobj=io.BytesIO(raw_bytes)) as gz:
            return gz.read().decode(encoding)

    # 异步下载大文件
    async def download_file(self, bucket: str, key: str, local_path: str):
        await self.initialize_class_variable()
        async with self.boto_session.client("s3", endpoint_url=self.endpoint_url, config=self.config) as s3:
            response = await s3.get_object(Bucket=bucket, Key=key)
            body = response["Body"]

            # 用异步方式写入本地
            async with aiofiles.open(local_path, "wb") as f:
                while True:
                    chunk = await body.read(10 * 1024 * 1024)  # 每次读 10MB
                    if not chunk:
                        break
                    await f.write(chunk)

        return local_path

    async def list_files(self, bucket: str, prefix: str, recursive: bool = True):
        """
        获取 bucket 下某个“目录”(prefix) 的文件列表

        单文件返回样例 ['server_data/api-title-roc/py_full_organ_dic/', 'server_data/api-title-roc/py_full_organ_dic/part-00000.gz']

        :param bucket: bucket 名
        :param prefix: 目录前缀，如 'server_data/api-title-roc/'
        :param recursive: 是否递归子目录
        :return: List[str] 文件 key 列表
        """
        await self.initialize_class_variable()
        keys = []

        # 非递归时，用 delimiter 模拟目录
        extra_args = {}
        if not recursive:
            extra_args["Delimiter"] = "/"

        async with self.boto_session.client(
                "s3",
                endpoint_url=self.endpoint_url,
                config=self.config
        ) as s3:

            continuation_token = None

            while True:
                kwargs = {
                    "Bucket": bucket,
                    "Prefix": prefix,
                    **extra_args
                }
                # 下一页的“游标”
                if continuation_token:
                    kwargs["ContinuationToken"] = continuation_token

                resp = await s3.list_objects_v2(**kwargs)

                # 文件
                for obj in resp.get("Contents", []):
                    keys.append(obj["Key"])

                # 是否还有下一页
                if resp.get("IsTruncated"):  # 说明还有下一页
                    # 下一页从哪里继续查
                    continuation_token = resp.get("NextContinuationToken")
                else:
                    break

        return keys
