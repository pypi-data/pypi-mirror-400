import requests

from .baai_config import DATACUBE_HOME, config_update

def login(ak, sk, login_api):

    save_name = DATACUBE_HOME / "config.json"

    headers = {
        "Accept-Language": "zh-CN",
        "Content-Type": "application/json",
    }
    resp = requests.post(login_api, json={"accessKey": ak, "secretKey": sk}, headers=headers)

    if resp.status_code != 200:
        print("登录失败")

    if resp.json().get("code") == 0:
        print(f"登录成功: config_path: {save_name.resolve()}")
    else:
        print("登录失败")

    token_data = {
        "access_key": ak,
        "secret_key": sk,
    }

    config_update(token_data)

