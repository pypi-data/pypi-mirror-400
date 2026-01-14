from jcclang.tests.remotefile.driver import RemoteFile, LocalDriver, HTTPRangeDriver


def choose_driver(url: str):
    if url.startswith("file://"):
        return LocalDriver()
    elif url.startswith("http://") or url.startswith("https://"):
        return HTTPRangeDriver()
    else:
        raise ValueError(f"Unsupported URL: {url}")


class JCWeaverTFDataset:
    def __init__(self, urls, decode_fn=None):
        """
        :param urls: 数据文件列表（支持 file://, http://, https://）
        :param decode_fn: 解码函数 (bytes -> tensor)
        """
        self.urls = urls
        self.decode_fn = decode_fn

    def generator(self):
        for url in self.urls:
            driver = choose_driver(url)
            f = RemoteFile(url, driver)
            raw = f.read()
            f.close()
            yield self.decode_fn(raw) if self.decode_fn else raw

    def to_tf_dataset(self, output_types=None, output_shapes=(), batch_size=32):
        # 延迟导入 TensorFlow，避免在模块加载时就依赖 TensorFlow
        print("start to_tf_dataset")
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError("TensorFlow is required for JCWeaverTFDataset")

        # 延迟设置默认值
        if output_types is None:
            output_types = tf.string

        print(f"output_types: {output_types}, output_shapes: {output_shapes}")
        return tf.data.Dataset.from_generator(
            self.generator,
            output_types=output_types,
            output_shapes=output_shapes
        ).batch(batch_size)
