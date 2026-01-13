import time
import traceback
import functools
import logging


Logger = logging.getLogger(__name__)


def retry(max_retries=3, retry_delay=1):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试间隔时间(秒)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            func_name = func.__name__

            for idx, attempt in enumerate(range(max_retries + 1)):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Logger.warning(f"{func_name}, 第{attempt + 1}次调用失败: {e}")
                        time.sleep(retry_delay * 2 * (idx+1))
                    else:
                        traceback.print_exc()
                        Logger.warning(f"{func_name}, 所有重试均失败，共尝试{max_retries + 1}次: {e}")
            # 抛出最后一次异常
            raise last_exception
        return wrapper

    return decorator

