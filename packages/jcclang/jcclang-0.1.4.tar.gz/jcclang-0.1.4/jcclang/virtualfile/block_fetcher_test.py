import os

from jcclang.virtualfile.block_fetcher import BlockFetcher
from jcclang.virtualfile.driver.jcs import JCS


def test_fetch_block():
    os.environ["SERVER_URL"] = "http://localhost:7891"
    os.environ["USER_ID"] = "3"

    driver = JCS(object_id=98)
    bf = BlockFetcher(driver=driver)
    data = bf.fetch_block(file_id="98", block_index=0)
    print(str(data))
    print()
