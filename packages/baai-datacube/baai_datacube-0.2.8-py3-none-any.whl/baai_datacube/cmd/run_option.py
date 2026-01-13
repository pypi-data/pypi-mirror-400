import os
import argparse
import pathlib
import traceback

from ..datacube_print import print_figlet
from ..baai_environment import setup_network


print_figlet()

datacube_home = pathlib.Path(os.path.expanduser("~")) / ".cache" / "datacube"
datacube_home.parent.mkdir(parents=True, exist_ok=True)


def runcmd_args(cmd_args=None):

    root_parser = argparse.ArgumentParser(add_help=False)
    root_parser.add_argument('--host', type=str, default="https://datacube.baai.ac.cn/api", help='服务地址')

    parser = argparse.ArgumentParser(prog='baai-datacube', description="数据魔方命令行工具")

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command')

    login_parser = subparsers.add_parser('login', help='登录数据魔方', parents=[root_parser])
    login_parser.set_defaults(func=login)

    down_parser = subparsers.add_parser('down', help='下载数据', parents=[root_parser])
    down_parser.set_defaults(func=down)
    down_parser.add_argument('--dataset', type=str, help='下载的数据集')
    down_parser.add_argument('-t', '--save-path', type=str, default=".", help='保存路径(默认当前文件夹)')
    down_parser.add_argument('--jobs', type=int, default=8, help='任务数')

    upload_parser = subparsers.add_parser('up', help='上传数据集', parents=[root_parser])
    upload_parser.add_argument('--collection', default=1,  type=int, help='下载的数据集')
    upload_parser.add_argument('-t', '--from-path', type=str, default=".", help='需要上传视频目录的文件')
    upload_parser.add_argument('--jobs', type=int, default=5, help='任务数')
    upload_parser.set_defaults(func=up)

    # 网络切换
    setup_network(cmd_args)

    # 解析命令行参数
    cmd_args = parser.parse_args()
    if hasattr(cmd_args, 'func'):
        try:
            cmd_args.func(cmd_args)
        except Exception: # noqa
            pass
        except KeyboardInterrupt:
            print()
            pass

    else:
        parser.print_help()


def login(cmd_args):
    from ..baai_login import login as login_user
    from ..baai_config import config_read

    config_default = config_read()
    host = config_default.get("host", cmd_args.host)

    print("---- login ----")

    ak = input(f"请输入ak [{config_default.get("access_key", "-")}]: ") or config_default.get("access_key")
    sk = input(f"请输入sk [{config_default.get("secret_key", "-")}]: ") or config_default.get("secret_key")
    login_api = f"{host}/auth/user-access-key-login"
    if not host.startswith("https"):
        print(f"login_api: {login_api}")
    login_user(ak, sk, login_api)


def down(cmd_args):
    from ..baai_meta import download_meta
    from ..baai_download import dataset_download

    save_path = pathlib.Path(cmd_args.save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    print("---- download ----")

    dataset_meta = download_meta(cmd_args.dataset, host=cmd_args.host)
    meta_path = (save_path / f"{cmd_args.dataset}.bin")

    with open(meta_path, "w") as f:
        f.write(dataset_meta)

    dataset_download(
        dataset_id=cmd_args.dataset,
        save_path=save_path.resolve().__str__(),
        meta_path=meta_path.resolve().__str__(),
        jobs=cmd_args.jobs
    )


def up(cmd_args):

    print("\n---- upload ----\n")

    import pathlib
    try:
        from ..baai_uploader import data_uploader
        from ..baai_config import Application

        config = Application(host=cmd_args.host)

        config.try_login()

        if not config.req_host.startswith("https"):
            print(f"host: {config.req_host}\n")

        data_uploader(cmd_args.collection, pathlib.Path(cmd_args.from_path), cmd_args.jobs)
    except Exception: # noqa
        traceback.print_exc()
