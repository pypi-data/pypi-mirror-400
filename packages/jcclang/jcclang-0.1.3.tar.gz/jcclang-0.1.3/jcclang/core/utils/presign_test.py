
import requests

from jcclang.core.utils.presign import SignKey, Presigner


def test_presign():
    sk = SignKey("XEVUusEUeyWqrBpdobcLrg==", "8EjWjDzjAwtPkF6vl0HgYk0SeDsbxDFE55EDgHGUlJM=")
    presigner = Presigner("https://121.36.5.116:32200", sk)

    params = {
        "objectID": 33186,
        "offset": 0,
        "length": 1024,
    }
    signed_url = presigner.presign(params, "/presigned/object/download", "GET", 3600)
    print(signed_url)
    session = requests.Session()

    resp2 = session.get(signed_url, stream=True, verify=False)
    if resp2.status_code != 200:
        print(resp2.status_code)
        print(resp2.text)
        exit(1)
    # 将resp2.content写入到文件中
    with open('C:\\Users\\27081\\AppData\\Local\\Temp\\jcweaver_diskcache\\nb15\\introduce.txt', 'wb') as f:
        for chunk in resp2.iter_content(chunk_size=4 * 1024):
            if chunk:
                f.write(chunk)
