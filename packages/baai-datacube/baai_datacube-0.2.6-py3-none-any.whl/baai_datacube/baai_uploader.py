import time
import logging
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

from .core import baai_write, baai_etag, baai_presign
from .helper import baai_vedio, baai_scanner
from .baai_config import Application


Logger = logging.getLogger(__name__)

stop_event = threading.Event()


def data_uploader(collection, upload_path=".", job_workers=5):
    # 环境变量
    collection_id = collection
    try:

        video_count = sum(1 for _ in baai_scanner.scan_all_folders_with_rglob(upload_path))

        # 线程池环境
        start = time.time()
        tasks = []
        executor = ThreadPoolExecutor(max_workers=job_workers)
        bar_format= "[{elapsed}] | {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt}{postfix} [{desc}: {rate_fmt}]"
        with tqdm(ncols=100, ascii="░▒▓█", total=video_count, desc="", position=0, leave=True, bar_format=bar_format) as pbar:
            for video_number, video_path in enumerate(baai_scanner.scan_all_folders_with_rglob(upload_path)):
                try:
                    pbar_idx = video_number % 5 + 1
                    task_worker = executor.submit(multipart_uploader, video_path, pbar_idx+1, collection_id)
                    tasks.append(task_worker)
                except Exception as e:
                    traceback.print_exc()
                    Logger.error(e)

            completed_count = 0
            for task in as_completed( tasks):
                try:
                    success_count = task.result()
                    completed_count += success_count
                except Exception as e:
                    traceback.print_exc()
                    Logger.error(e)
                finally:
                    pbar.update(1)

        end = time.time()
        print()
        print(f"Success: {completed_count}, Fail: {video_count - completed_count}, Total {video_count}")
        print()
        print(f"{end - start:.2f}s")

    except KeyboardInterrupt:
        import os


        app = Application()
        req_headers = {
            "Authorization": f"Bearer {app.try_login()}",
        }

        host = app.req_host

        requests.put(
            f"{host}/storage/upload/{collection_id}",
            headers=req_headers,
            json={
                "status": "cancelled",
            }
        )

        print("=================已经取消上传==================")
        # TODO

        os._exit(1)

    except Exception as e:
        traceback.print_exc()
        print(e)
    else:

        app = Application()
        req_headers = {
            "Authorization": f"Bearer {app.try_login()}",
        }

        host = app.req_host

        requests.put(
            f"{host}/storage/upload/{collection_id}",
            headers=req_headers,
            json={
                "status": "completed",
            }
        )

    finally:
        pass


def multipart_uploader(video_path, video_number, collection_id):
    try:

        # 获取视频时长
        try:
            video_duration = int(baai_vedio.get_video_duration(video_path))
        except Exception as e:
            print(video_path.name, e)
            return 0

        size = video_path.stat().st_size
        etag = baai_etag.etag_write(video_path, size)


        # 创建上传的文件信息
        sign_data, upload_id, upload_size = baai_write.sign_write(collection_id, f"{video_path.name}", size, etag, video_duration)

        # 检查是否上传完成
        if upload_size == size:
            return 1
        else:
            upload_id, upload_parts = baai_presign.write_multipart(sign_data, upload_id=upload_id)

        if not upload_id:
            upload_id, upload_parts = baai_presign.write_multipart(sign_data)

        if not upload_id:
            return 0

        # 上传所有分片
        e_tags = baai_write.multipart_upload(
            collection_id,  # 数据集信息
            etag, size,  # 文件信息
            video_path, # 文件路径
            sign_data,  # 签名数据
            upload_id,  # 上传信息
            upload_parts, # 上传的分片信息
            video_number, # 分片ID
            video_path.name, # 文件名字
            stop_event
        )

        # 完成分片上传
        baai_presign.write_multipart(sign_data, upload_id, e_tags)
    except Exception: # noqa
        traceback.print_exc()
        return 0
    else:
        # 成功增加完成量
        return 1
