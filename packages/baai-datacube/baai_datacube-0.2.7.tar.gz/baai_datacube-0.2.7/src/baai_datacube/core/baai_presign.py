import requests


from pyrate_limiter import Rate, Duration, Limiter

from ..baai_config import Application

from .baai_retry import retry


# 存储相关的服务地址
# STORAGE = "http://127.0.0.1:31000"
# STORAGE = "http://120.92.15.143/api"

# 控制签名速度
LIMITER = Limiter(Rate(20, Duration.SECOND * 1), max_delay=10000)


@retry(max_retries=3)
def write_presign(sign_data, upload_id, idx):
    config = Application()

    post_data = {
        "upload_sign": sign_data,
        "upload_id": upload_id,
        "upload_num": idx + 1,
        "network": config.network
    }

    host = config.req_host

    sign_api = f"{host}/v1/storage/upload/presign"
    resp_sign = requests.post(sign_api, json=post_data)

    assert resp_sign.status_code == 200 and resp_sign.json().get("code") == 0, resp_sign.text

    # 成功限制速度
    LIMITER.try_acquire("write_presign")

    return resp_sign.json().get("data").get("endpoint")



@retry(max_retries=3)
def write_multipart(sign_data, upload_id=None, etags=None):
    """write multipart

    分片上传的开始与结束(when upload_id not none and all etags)

    场景:
    1. upload_id: none, 创建 upload_id
    2. upload_id: v, etags: none, 获取以及上传的分片信息
    3. upload_id: v, etags: v, 合并分片完成上传
    """


    config = Application()
    post_data = {"upload_sign": sign_data}

    if upload_id:
        post_data.update({"upload_id": upload_id})

    if etags:
        post_data.update({"upload_parts": etags})

    host = config.req_host
    multipart_api = f"{host}/v1/storage/upload/multipart"
    resp_multipart = requests.post(multipart_api, json=post_data, timeout=5)

    assert resp_multipart.status_code == 200, resp_multipart.text
    resp_data = resp_multipart.json().get("data")
    upload_id = resp_data.get("upload_id")
    upload_parts = resp_data.get("upload_parts")
    return upload_id, upload_parts


@retry(max_retries=10)
def write_multipart_data(
    write_bytes, sign_data, upload_id, idx,
):
    """write_multipart_data

    上传分片数据
    """

    # presign
    write_endpoint = write_presign(sign_data, upload_id, idx)

    # write
    resp_write = requests.put(write_endpoint, data=write_bytes)
    e_tag = resp_write.headers.get("ETag")

    # 判断是否上传成功
    assert resp_write.status_code == 200

    return e_tag, len(write_bytes)
