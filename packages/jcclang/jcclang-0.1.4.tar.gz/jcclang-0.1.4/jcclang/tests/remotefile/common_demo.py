from jcclang.tests.remotefile.common_dataset import load_dataset


def decode_text(raw: bytes):
    return raw.decode("utf-8")


urls = [
    # "file:///tmp/test1.txt",
    "http://121.36.5.116:32010/object/download?userID=5&objectID=157109"
]

dataset = load_dataset(urls, framework="torch", decode_fn=decode_text, batch_size=2)


def test_tf_demo():
    from jcclang.tests.remotefile.tensorfflow_demo import test_tf_demo
    test_tf_demo()
