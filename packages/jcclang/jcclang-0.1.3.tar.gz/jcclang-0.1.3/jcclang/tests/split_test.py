from urllib.parse import urlparse, parse_qs


def test_split():
    url = "http://localhost:7891/api/workflow?packageID=1&token=1234567890"
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    package_id = params['packageID'][0]  # 获取 packageID 的值: "1"
    token = params['token'][0]           # 获取 token 的值: "1234567890"

    print("packageID:", package_id)
    print("token:", token)

    token = url.split("?")[0]
    print(token)
