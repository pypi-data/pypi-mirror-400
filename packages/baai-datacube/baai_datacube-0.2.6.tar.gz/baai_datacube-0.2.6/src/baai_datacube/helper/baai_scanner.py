from pathlib import Path


def scan_all_folders_with_rglob(root_path):
    """使用rglob获取所有文件夹"""
    root = Path(root_path)

    # 使用rglob('*')递归匹配所有路径，然后筛选出目录
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        yield p

