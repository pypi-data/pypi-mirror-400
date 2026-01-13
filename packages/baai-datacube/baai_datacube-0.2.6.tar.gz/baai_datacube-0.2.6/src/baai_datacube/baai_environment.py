import requests

from .baai_config import config_update

def setup_network(cmd_args):
    try:
        private = "https://baai-datasets.ks3-cn-beijing-internal.ksyuncs.com/public/internal/speed/readme.md"
        requests.get(private, timeout=1)
    except requests.exceptions.ReadTimeout:
        network = "public"
    except Exception as e:
        print(e)
        network = "public"
    else:
        network = "private"

    config_data = {
        "network": network,
    }

    print("network: ", network)
    config_update(config_data)
