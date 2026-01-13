"""
阿里云OSS工具类
"""
import os
import tempfile
import time
from typing import Union, Dict, Optional
from urllib.parse import urlparse, unquote

import oss2

from .logger import logger


class OSSUtil:
    """阿里云OSS上传下载工具类"""
    
    def __init__(self):
        endpoint = os.getenv("OSS_ENDPOINT")
        access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
        access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
        bucket_name = os.getenv("OSS_BUCKET_NAME")
        
        if not all([endpoint, access_key_id, access_key_secret, bucket_name]):
            raise ValueError("OSS配置不完整，请检查环境变量: OSS_ENDPOINT, OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_BUCKET_NAME")
        
        self.endpoint = endpoint
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.bucket_name = bucket_name
        self.url_expire = int(os.getenv("OSS_URL_EXPIRE", "604800"))
        
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    def upload_file_with_task_info(self, file: Union[str, bytes], task_id: str, task_type: str, file_name: str) -> Dict[str, str]:
        """
        上传文件到OSS
        
        Args:
            file: 文件路径、文件内容字符串或二进制内容
            task_id: 任务ID
            task_type: 任务类型
            file_name: 文件名
            
        Returns:
            包含url和oss_key的字典
        """
        oss_key = f"{task_type}/{task_id}/{file_name}"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if isinstance(file, str) and os.path.exists(file):
                    self.bucket.put_object_from_file(oss_key, file)
                elif isinstance(file, (str, bytes)):
                    if isinstance(file, str):
                        file = file.encode('utf-8')
                    self.bucket.put_object(oss_key, file)
                else:
                    raise TypeError("file必须是文件路径字符串、字符串内容或二进制内容")
                
                url = self.generate_url(oss_key)
                logger.info(f"{task_id} 上传文件到OSS完成: oss_key=\"{oss_key}\", url=\"{url}\"")
                return {"url": url, "oss_key": oss_key}
            except oss2.exceptions.OssError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"{task_id} 上传文件到OSS失败: oss_key=\"{oss_key}\", error=\"{str(e)}\"")
                    raise

    def download_file(self, remote_path: str, local_file_path: Optional[str] = None) -> str:
        """
        从OSS下载文件
        
        Args:
            remote_path: OSS路径或完整URL
            local_file_path: 本地保存路径，为None时使用临时目录
            
        Returns:
            本地文件路径
        """
        if remote_path.startswith("http://") or remote_path.startswith("https://"):
            parsed_url = urlparse(remote_path)
            oss_key = unquote(parsed_url.path.lstrip('/'))
        else:
            oss_key = remote_path
        
        if not oss_key:
            raise ValueError("remote_path格式无效或为空")
        
        if local_file_path is None:
            filename = os.path.basename(oss_key)
            local_file_path = os.path.join(tempfile.gettempdir(), filename)
        
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        self.bucket.get_object_to_file(oss_key, local_file_path)
        logger.info(f"从OSS下载文件完成: oss_key=\"{oss_key}\", local_path=\"{local_file_path}\"")
        return local_file_path

    def generate_url(self, oss_key: str, expiration: Optional[int] = None) -> str:
        """
        生成公开访问URL（无签名）
        
        Args:
            oss_key: OSS对象键
            expiration: 过期时间（秒），此参数在公开URL中不使用
            
        Returns:
            公开访问URL
        """
        if expiration is None:
            expiration = self.url_expire
        
        url = f"https://{self.bucket_name}.{self.endpoint.replace('http://', '').replace('https://', '')}/{oss_key}"
        return url

    def generate_signed_url(self, oss_key: str, expiration: Optional[int] = None) -> str:
        """
        生成带签名的访问URL
        
        Args:
            oss_key: OSS对象键
            expiration: 过期时间（秒）
            
        Returns:
            签名URL
        """
        if expiration is None:
            expiration = self.url_expire
        
        signed_url = self.bucket.sign_url('GET', oss_key, expiration)
        return signed_url

