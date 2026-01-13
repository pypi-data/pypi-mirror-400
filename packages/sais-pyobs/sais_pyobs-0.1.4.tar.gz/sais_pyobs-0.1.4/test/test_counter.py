import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import unittest
from io import BytesIO
from pyobs.core import StreamUploader, UploadContext

# Mock ObsClient
class MockObsClient:
    def __init__(self, *args, **kwargs):
        pass
    def uploadPart(self, *args, **kwargs):
        class Resp:
            status = 200
            class Body:
                etag = "mock_etag"
            body = Body()
        return Resp()
    def listParts(self, *args, **kwargs):
        class Resp:
            status = 200
            class Body:
                parts = []
                isTruncated = False
            body = Body()
        return Resp()
    def completeMultipartUpload(self, *args, **kwargs):
        class Resp:
            status = 200
        return Resp()

class TestStreamCounter(unittest.TestCase):
    def test_byte_counting(self):
        # 1. Mock 环境
        uploader = StreamUploader(ak="test", sk="test", server="test", bucket_name="test")
        uploader.client = MockObsClient()
        # 调小分片大小以便触发分片逻辑
        uploader.part_size = 10 
        uploader.max_workers = 1

        # 2. 构造 100 字节的数据流
        total_data = b"a" * 105
        def data_stream():
            # 分 11 次 yield，每次 10 字节，最后一次 5 字节
            chunk_size = 10
            for i in range(0, len(total_data), chunk_size):
                yield total_data[i:i+chunk_size]

        # 3. 执行 _process_stream
        # 模拟一个新任务 context
        uid = "test_upload_id"
        key = "test_key"
        
        # 这里的 total_size 仅用于进度条，不影响统计逻辑
        uploaded_bytes = uploader._process_stream(
            iterator=data_stream(),
            key=key,
            uid=uid,
            start_part=1,
            total_size=len(total_data)
        )

        print(f"预期字节数: {len(total_data)}")
        print(f"实际统计数: {uploaded_bytes}")

        self.assertEqual(uploaded_bytes, len(total_data))

if __name__ == '__main__':
    unittest.main()
