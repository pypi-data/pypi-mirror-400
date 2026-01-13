import requests
from tqdm import tqdm
from obs_file import open, getsize
import os
import time
object_key = 'test/2018_03_public1.txt'
bucket = 'sais-craw-v2'
block_size = 10 * 1024 * 1024  # 10MB
os.environ["OBS_ACCESS_KEY"] = "OEIXE6THI9OSTPBNUTY8"
os.environ["OBS_SECRET_KEY"] = "lNHJhr306Qt5iHS73F3KZqOdT2mTRQdI2qMMMHOX"
os.environ["OBS_SERVER"] = "https://obs.cn-east-3.myhuaweicloud.com"
t = time.time()
# 获取已上传的大小
def format_file_size(size_bytes: int) -> str:
    """将字节数格式化为人类可读的格式"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


try:
    start_size = getsize(bucket, object_key)
except FileNotFoundError:
    start_size = 0
s=format_file_size(size_bytes=start_size)
print(f"文件大小: {s} ")
# 添加Range头，从已上传的大小开始下载
headers = {}
if start_size > 0:
    headers['Range'] = f'bytes={start_size}-'

# 发送HTTP请求
response = requests.get('https://jeodpp.jrc.ec.europa.eu/ftp/public/MachineLearning/SatImNet/BigEarthNet-v1.0/2018_03_public.txt', stream=True, headers=headers)
# response.raise_for_status()

# 打开OBS文件进行写入
with open(bucket, object_key, 'ab', part_size=20*1024*1024) as obs_file:
    # 使用tqdm创建进度条
    with tqdm( unit='B', unit_scale=True) as pbar:
        # 流式下载并直接写入OBS
        for data in response.iter_content(chunk_size=10*1024*1024):
            if data:  # 过滤掉keep-alive的空数据包
                obs_file.write(data)
                pbar.update(len(data))
        # 完成上传
        obs_file.complete()

print(time.time()-t)