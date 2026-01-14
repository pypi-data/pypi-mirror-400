import tensorflow as tf
from jcclang.core.model import Sources, VirtualFileParams
from jcclang.virtualfile.virtual_file import VirtualFile


class Dataset:
    def __init__(self, sources: Sources, decoder=None,
                 virtual_file_params: VirtualFileParams = None):
        """
        :param sources: Sources 对象
        :param decode_fn: 数据解码函数，输入 raw bytes，输出 numpy / tensor
        :param virtual_file_params: 虚拟文件参数
        """
        if virtual_file_params is None:
            virtual_file_params = VirtualFileParams()
        self.virtual_file_params = virtual_file_params
        self.sources = sources
        self.decode_fn = decoder or (lambda x: x)  # 默认不解码

    def generator(self):
        """
        数据生成器，每次 yield (sample, label)
        """
        for info in self.sources.items:
            # 读取数据
            vf = VirtualFile(info, params=self.virtual_file_params)
            raw = vf.read()
            vf.close()

            # 解码
            sample = self.decode_fn(raw)

            # 输出 sample 和 label
            yield sample, info.label

    def to_tf_dataset(self, output_types=tf.float32, output_shapes=None, batch_size=32, shuffle=True):
        """
        转为 tf.data.Dataset
        :param output_types: 输出类型，可以是 tf.float32, tf.int32 等
        :param output_shapes: 输出形状，如 (28,28) 或 (None,)
        :param batch_size: 批大小
        :param shuffle: 是否打乱
        """
        ds = tf.data.Dataset.from_generator(
            self.generator,
            output_types=(output_types, tf.int32),
            output_shapes=(output_shapes, ())
        )
        if shuffle:
            ds = ds.shuffle(buffer_size=len(self.sources.items))
        ds = ds.batch(batch_size)
        ds = ds.prefetch(tf.data.AUTOTUNE)
        return ds
