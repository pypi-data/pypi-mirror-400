import os
import time
import logging
import traceback
from concurrent.futures import wait, FIRST_COMPLETED

import requests
from tqdm import tqdm

from .core import baai_write, baai_etag, baai_presign, baai_concurrent
from .helper import baai_vedio, baai_scanner
from .baai_config import Application


Logger = logging.getLogger(__name__)


def data_uploader(collection, upload_path=".", job_workers=5):
    # 环境变量
    collection_id = collection
    try:

        video_count = sum(1 for _ in baai_scanner.scan_all_folders_with_rglob(upload_path))

        # 线程池环境
        start = time.time()
        tasks = []

        worker_pool = baai_concurrent.ThreadPoolExecutor(max_workers=job_workers)
        writer_pool = baai_concurrent.ThreadPoolExecutor(max_workers=job_workers*2)

        bar_format= "[{elapsed}] | {percentage:5.1f}%|{bar}| {n_fmt}/{total_fmt}{postfix}"
        with tqdm(ncols=120, ascii="░▒▓█", total=video_count, desc="", position=0, leave=True, bar_format=bar_format) as pbar:
            for video_number, video_path in enumerate(baai_scanner.scan_all_folders_with_rglob(upload_path)):
                try:
                    pbar_idx = video_number % 5 + 1
                    task_worker = worker_pool.submit(
                        multipart_uploader,
                        video_path, pbar_idx+1, collection_id, writer_pool
                    )
                    tasks.append(task_worker)
                except Exception as e:
                    traceback.print_exc()
                    Logger.error(e)

            completed_count = 0
            pending = set(tasks)  # 所有 futures

            try:
                while pending:
                    done, pending = wait(pending, timeout=0.5, return_when=FIRST_COMPLETED)
                    for task in done:
                        try:
                            success_count = task.result()
                            completed_count += success_count
                        except Exception as e:
                            traceback.print_exc()
                            Logger.error(e)
                        finally:
                            pbar.update(1)
            except KeyboardInterrupt:
                # writer_pool.shutdown(wait=False, cancel_futures=True)
                # worker_pool.shutdown(wait=False, cancel_futures=True)
                raise

        end = time.time()
        print()
        print(f"Success: {completed_count}, Fail: {video_count - completed_count}, Total {video_count}")
        print()
        print(f"{end - start:.2f}s")

    except KeyboardInterrupt:

        app = Application()
        req_headers = {
            "Authorization": f"Bearer {app.try_login()}",
        }

        host = app.req_host

        # TODO: 增加重试
        requests.put(
            f"{host}/storage/upload/{collection_id}",
            headers=req_headers,
            json={
                "status": "cancelled",
            }
        )


        print("\n\n\n\n\n\n\n\n\n\n\n")
        print("=================已经取消上传==================")
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


def multipart_uploader(video_path, video_number, collection_id, writer_executor):
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
            writer_executor # 写入线程池
        )

        # 完成分片上传
        baai_presign.write_multipart(sign_data, upload_id, e_tags)
    except Exception: # noqa
        traceback.print_exc()
        return 0
    else:
        # 成功增加完成量
        return 1
