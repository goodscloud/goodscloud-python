import sys

from goodscloud_api_client.client import GoodsCloudAPIClient


def get_company():
    gc = GoodsCloudAPIClient(
        host=sys.argv[1],
        user=sys.argv[2],
        pwd=sys.argv[3],
    )
    response = gc.get("internal/company")
    resp_json = response.json()
    print resp_json


if __name__ == '__main__':
    get_company()
