# Huace AIGC Frame

华策AIGC框架 - 阿里云OSS工具包

## 安装

```bash
pip install huace-aigc-frame
```

## 使用方法

### 配置环境变量

```bash
export OSS_ENDPOINT=your-endpoint
export OSS_ACCESS_KEY_ID=your-access-key-id
export OSS_ACCESS_KEY_SECRET=your-access-key-secret
export OSS_BUCKET_NAME=your-bucket-name
export OSS_URL_EXPIRE=604800  # 可选，默认7天
```

### 基本使用

```python
from huace_aigc_frame import OSSUtil

# 初始化
oss = OSSUtil()

# 上传文件
result = oss.upload_file_with_task_info(
    file="path/to/file.txt",
    task_id="task123",
    task_type="image",
    file_name="result.txt"
)
print(result["url"])

# 下载文件
local_path = oss.download_file("https://bucket.endpoint/path/to/file.txt")

# 生成签名URL
signed_url = oss.generate_signed_url("path/to/file.txt", expiration=3600)
```

## 功能特性

- 文件上传（支持文件路径、字符串内容、二进制内容）
- 文件下载
- URL生成（公开和签名）
- 自动重试机制
- 完善的日志记录

## 依赖

- Python >= 3.7
- oss2 >= 2.17.0

## License

MIT

