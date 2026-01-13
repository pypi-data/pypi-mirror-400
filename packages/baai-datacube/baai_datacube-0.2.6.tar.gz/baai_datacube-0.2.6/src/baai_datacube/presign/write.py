import datetime
import hashlib
import msgpack
import base64
import jwt


def jwtsign_create(proto, prefix, path, check_point, secret="secret"):
    """jwtsign_create

    创建用户需要上传云存储的数据签名
    """

    check_point = hashlib.md5(check_point.encode("utf-8")).hexdigest()

    upload_pack = msgpack.dumps(
        {"proto":proto, "prefix": prefix, "path": path},
    )
    upload_path = base64.b64encode(upload_pack).decode("utf-8")

    payload = {
        "upload_path": upload_path,
        "check_point": check_point,
        "stamp": int(datetime.datetime.now().timestamp()),
    }
    download_sign = jwt.encode(payload, secret, algorithm="HS256")


    return download_sign


if __name__ == "__main__":

    import  requests

    sign_data = jwtsign_create("ks3://baai-data-label", "202511261801", "test.txt", "127.0.0.1")


    resp_multipart = requests.post(
        "http://127.0.0.1:31000/v1/storage/upload/multipart",
        json={
            "upload_sign": sign_data,
        }
    )

    print(resp_multipart.status_code)
    print(resp_multipart.text)
    print("============="* 100)

    upload_id = resp_multipart.json().get("data").get("upload_id")
    resp = requests.post(
        "http://127.0.0.1:31000/v1/storage/upload/presign",
        json={
            "upload_sign": sign_data,
            "upload_id": upload_id,
            "upload_num": 1,
            "network": "public"
        }
    )

    print(resp.status_code)
    print(resp.text)

    print("============="* 100)

    with open("/Users/hgshicc/Downloads/s3_paths.txt", "rb") as f:
        resp_write = resp_upload = requests.put(
            resp.json().get("data").get("endpoint"),
            data=f
        )

        print(resp_write.status_code)
        for k, v in resp_write.headers.items():
            print(k, v)

    e_tag = resp_write.headers.get("ETag")

    print("============="* 100)
    resp_complete = resp_multipart = requests.post(
        "http://127.0.0.1:31000/v1/storage/upload/multipart",
        json={
            "upload_sign": sign_data,
            "upload_id": upload_id,
            "upload_parts": [e_tag]
        }
    )
    print(resp_complete.status_code)


