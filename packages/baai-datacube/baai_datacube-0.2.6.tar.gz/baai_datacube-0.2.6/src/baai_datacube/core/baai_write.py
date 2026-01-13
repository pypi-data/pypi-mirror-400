import atexit
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from tqdm import tqdm


from ..baai_config import Application
from . import baai_presign, baai_retry


# 签名服务
# WRITE_ENDPOINT = "http://127.0.0.1:30201"
# WRITE_ENDPOINT = "http://120.92.15.143/api"

# 上传块大小
CHUNK_SIZE = 1024 * 1024 * 5
write_pool = ThreadPoolExecutor(max_workers=10)


@baai_retry.retry(max_retries=3)
def sign_write(collection_id, file_name, file_size, file_etag, video_duration):
    """sign_write

    文件上传签名，如果文件上传了一部分，使用返回的数据进行断点续传
    """

    app = Application()
    req_headers = {
        "Authorization": f"Bearer {app.try_login()}",
    }

    req_host = app.req_host

    try:
        resp_sign = requests.post(
            f"{req_host}/collection/file/create",
            headers=req_headers,
            json={
                "fileEtag": file_etag,
                "collectionId": collection_id,
                "fileName": file_name,
                "fileSize": file_size,
                "videoDuration": video_duration
            }, timeout=(1, 5)
        )

    except Exception as e:
        raise e
    else:
        assert resp_sign.status_code == 200 and resp_sign.json().get("code") == 0, resp_sign.text

        resp_data = resp_sign.json().get("data")
        sign_data = resp_data.get("uploadSign")

        return sign_data, resp_data.get("uploadId"), resp_data.get("uploadSize")


@baai_retry.retry(max_retries=3)
def update_write(collection_id, file_etag, file_size, upload_id=""):
    """update_write

    文件上传进度记录
    """


    app = Application()
    req_headers = {
        "Authorization": f"Bearer {app.try_login()}",
    }


    req_host = app.req_host

    resp_sign = requests.post(
        f"{req_host}/collection/file/update",
        headers=req_headers,
        json={
            "collectionId": collection_id,
            "fileEtag": file_etag,
            "uploadSize": file_size,
            "uploadId": upload_id
        }
    )

    assert resp_sign.status_code == 200 and resp_sign.json().get("code") == 0, resp_sign.text


def multipart_upload(
        collection_id, etag, size, video_path, sign_data,
        upload_id, upload_parts,
        video_number, video_name,
        stop_event
):

    e_tags =  []
    m_parts = {}
    if upload_parts:
        m_parts = { part.get("part_number")-1: part.get("e_tag") for part in upload_parts}

    total_length = 0
    tasks = []

    if len(video_name) > 18:
        desc_name = "..." + video_name[-15:]
    else:
        desc_name = video_name.rjust(18)

    with tqdm(total=size, unit='B', unit_scale=True, desc=desc_name, position=video_number, leave=False) as pbar:

        for idx, start_pos in enumerate(range(0, size, CHUNK_SIZE)):
            if stop_event.is_set():
                break

            end_pos = min(start_pos + CHUNK_SIZE, size)

            # 跳过已经上传的分片
            if e_tag := m_parts.get(idx+1):
                e_tags.append(e_tag)

                total_length += end_pos - start_pos
                update_write(collection_id, etag, end_pos, upload_id)

                pbar.update(end_pos - start_pos)
                continue

            # 读取分片数据,进行上传
            with video_path.open("rb") as reader:
                # prepare
                reader.seek(start_pos)
                write_bytes = reader.read(end_pos - start_pos)

                try:
                    task_write = write_pool.submit(baai_presign.write_multipart_data, write_bytes, sign_data, upload_id, idx)
                    tasks.append(task_write)
                except Exception as e:
                    raise e

        for task in as_completed(tasks):
            # TODO: 增加中断
            if stop_event.is_set():
                break

            try:
                e_tag, length = task.result()
                e_tags.append(e_tag)
                total_length += length
            except Exception as e:
                traceback.print_exc()
                print(e)
            else:
                update_write(collection_id, etag, total_length, upload_id)
                pbar.update(length)

    return e_tags
