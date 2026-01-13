from pyobs import StreamUploader
import requests
import time
# 1. 初始化 SDK
uploader = StreamUploader(
    ak="OEIXE6THI9OSTPBNUTY8",
    sk="lNHJhr306Qt5iHS73F3KZqOdT2mTRQdI2qMMMHOX",
    server="obs.cn-east-3.myhuaweicloud.com",
    bucket_name="sais-craw-v2"
)
t = time.time()
context = uploader.init_upload(object_key="test/2018_03_public.txt")

print(f"-> SDK 建议从 {context.offset} 字节处开始下载")

# 2. 根据 offset 发起下载
headers = {
    "Range": f"bytes={context.offset}-"  # <--- 关键
}

# stream=True 流式下载
response = requests.get("https://jeodpp.jrc.ec.europa.eu/ftp/public/MachineLearning/SatImNet/BigEarthNet-v1.0/2018_03_public.txt", headers=headers, stream=True)


# 3. 把流扔回给 SDK
uploader.upload_stream(
    context=context,
    stream_iterator=response.iter_content(chunk_size=10*1024*1024),
    mode='wb',
    total_size=3
)
print(time.time()-t)