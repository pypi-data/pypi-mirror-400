import tensorflow as tf

from jcclang.tests.remotefile.jcweaver_tf_dataset import JCWeaverTFDataset


def decode_text(raw: bytes):
    return raw.decode("utf-8")


urls = [
    "http://121.36.5.116:32010/object/download?userID=5&objectID=157109"
]


# def test_tf_demo():
#     print()
#     dataset = JCWeaverTFDataset(urls, decode_fn=decode_text).to_tf_dataset(
#         output_types=tf.string,
#         output_shapes=(),
#         batch_size=2
#     )
#     print("start111")
#     print()


if __name__ == '__main__':
    print(tf.__file__)
