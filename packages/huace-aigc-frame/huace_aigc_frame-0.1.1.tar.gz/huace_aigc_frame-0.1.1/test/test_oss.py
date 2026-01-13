"""
OSS工具类简单测试
"""
import os
import tempfile
from pathlib import Path


def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ 已加载环境配置: {env_path}")
        else:
            print(f"⚠ 未找到.env文件: {env_path}")
    except ImportError:
        print("⚠ python-dotenv未安装，使用系统环境变量")


def test_oss_util():
    """测试OSS工具类"""
    from huace_aigc_frame import OSSUtil
    
    print("\n" + "="*50)
    print("华策AIGC框架 - OSS工具测试")
    print("="*50)
    
    # 初始化
    try:
        oss = OSSUtil()
        print(f"✓ OSS初始化成功")
        print(f"  Endpoint: {os.getenv('OSS_ENDPOINT')}")
        print(f"  Bucket: {os.getenv('OSS_BUCKET_NAME')}")
    except Exception as e:
        print(f"❌ OSS初始化失败: {e}")
        return
    
    # 测试1: 上传文本内容
    print("\n--- 测试1: 上传文本内容 ---")
    try:
        result = oss.upload_file_with_task_info(
            file="测试文本内容",
            task_id="test_001",
            task_type="test",
            file_name="test.txt"
        )
        print(f"✓ 上传成功")
        print(f"  URL: {result['url']}")
        print(f"  Key: {result['oss_key']}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return
    
    # 测试2: 上传本地文件
    print("\n--- 测试2: 上传本地文件 ---")
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        temp_file.write("临时测试文件内容\n")
        temp_file.close()
        
        result2 = oss.upload_file_with_task_info(
            file=temp_file.name,
            task_id="test_002",
            task_type="test",
            file_name="local_file.txt"
        )
        print(f"✓ 上传成功")
        print(f"  URL: {result2['url']}")
        
        os.unlink(temp_file.name)
    except Exception as e:
        print(f"❌ 上传失败: {e}")
    
    # 测试3: 生成签名URL
    print("\n--- 测试3: 生成签名URL ---")
    try:
        signed_url = oss.generate_signed_url(result['oss_key'], expiration=3600)
        print(f"✓ 签名URL生成成功（1小时有效）")
        print(f"  URL: {signed_url[:80]}...")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
    
    # 测试4: 下载文件
    print("\n--- 测试4: 下载文件 ---")
    try:
        local_path = oss.download_file(result['url'])
        print(f"✓ 下载成功")
        print(f"  本地路径: {local_path}")
        
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  文件内容: {content}")
            os.unlink(local_path)
    except Exception as e:
        print(f"❌ 下载失败: {e}")
    
    print("\n" + "="*50)
    print("✓ 测试完成！")
    print("="*50)


if __name__ == "__main__":
    load_env()
    test_oss_util()

