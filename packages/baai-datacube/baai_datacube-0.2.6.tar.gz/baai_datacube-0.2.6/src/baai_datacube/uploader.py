import traceback
import pathlib


def dataset_upload(collection_id,  upload_path="."):
    from .baai_environment import setup_network

    setup_network(None)

    upload_path = pathlib.Path(upload_path)

    try:
        from .baai_uploader import data_uploader

        data_uploader(collection_id, upload_path)
    except Exception: # noqa
        traceback.print_exc()
