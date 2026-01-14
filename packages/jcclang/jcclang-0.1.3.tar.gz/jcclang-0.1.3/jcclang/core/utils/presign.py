import base64
import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

import requests

DATE_KEY = "X-JCS-Date"
EXPIRES_KEY = "X-JCS-Expires"
AUTHORIZATION_KEY = "X-JCS-Authorization"
ALGORITHM_VALUE = "JCS1-HMAC-SHA256"
DATE_FORMAT = "%Y%m%dT%H%M%SZ"


class SignKey:
    def __init__(self, access_key_id: str, secret_access_key: str):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key.encode()

    def presign_url(self, method: str, url_obj, signing_time: datetime, expires_seconds: int):
        date = signing_time.strftime(DATE_FORMAT)

        # 构建查询参数
        queries = dict(parse_qsl(url_obj.query))
        queries[DATE_KEY] = date
        queries[EXPIRES_KEY] = str(expires_seconds)

        # 构造 string to sign
        string_to_sign = make_string_to_sign(method, url_obj.path, queries, {}, "")

        # 计算 HMAC-SHA256 并 Base64
        signature = base64.b64encode(
            hmac.new(self.secret_access_key, string_to_sign.encode(), hashlib.sha256).digest()).decode()

        # 构造 Authorization 字符串
        auth_str = f"{ALGORITHM_VALUE} {self.access_key_id},{signature}"
        queries[AUTHORIZATION_KEY] = auth_str

        # 按 key 排序并编码
        sorted_items = sorted(queries.items())
        encoded_query = urlencode(sorted_items, doseq=True)

        # 返回最终 URL
        new_url = url_obj._replace(query=encoded_query)
        return urlunparse(new_url)


def make_string_to_sign(method, path, queries, headers, body_hash):
    # 方法
    lines = [method.upper()]

    # 路径
    if not path.startswith("/"):
        path = "/" + path
    lines.append(path)

    # 查询参数排序 + urlencode
    sorted_query_items = sorted(queries.items())
    query_str = urlencode(sorted_query_items, doseq=True)
    lines.append(query_str)

    # headers
    sorted_headers = sorted((k.lower(), v) for k, v in headers.items())
    for k, v in sorted_headers:
        lines.append(f"{k}:{v}")

    # body hash
    lines.append(body_hash)

    return "\n".join(lines)


class Presigner:
    def __init__(self, endpoint: str, sign_key: SignKey):
        self.endpoint = endpoint
        self.sign_key = sign_key

    def presign(self, req: dict, path: str, method: str, expire_in: int):
        url_obj = urlparse(self.endpoint)
        full_path = url_obj.path.rstrip("/") + "/v1/" + path.lstrip("/")
        url_obj = url_obj._replace(path=full_path)

        query_string = urlencode(req, doseq=True)
        url_obj = url_obj._replace(query=query_string)

        signed_url = self.sign_key.presign_url(method, url_obj, datetime.now(timezone.utc), expire_in)
        return signed_url
