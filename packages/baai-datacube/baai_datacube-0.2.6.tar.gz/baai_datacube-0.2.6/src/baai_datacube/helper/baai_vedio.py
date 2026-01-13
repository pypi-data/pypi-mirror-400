import cv2


def get_video_duration(video_path):
    """
    获取视频文件的时长（秒）
    返回值: 成功返回时长(秒)，失败返回None
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"错误：无法打开视频文件 {video_path}")
        return None

    # 获取关键属性
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 释放视频流
    cap.release()

    # 检查并计算时长
    if fps > 0 and total_frames > 0:
        duration_seconds = total_frames / fps
        return duration_seconds
    else:
        print("警告：无法获取有效的帧数或帧率。")
        return None
