import os

from jcclang.virtualfile.driver.jcs import JCS


def test_jcs():
    os.environ["SERVER_URL"] = "http://localhost:7891"
    os.environ["USER_ID"] = "3"
    driver = JCS(object_id=98)
    byte = driver.read()
    print(str(byte))
    print()
