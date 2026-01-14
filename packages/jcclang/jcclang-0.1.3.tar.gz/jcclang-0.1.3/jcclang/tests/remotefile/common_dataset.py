from typing import List, Callable, Optional


def load_dataset(
        urls: List[str],
        framework: str = "torch",
        decode_fn: Optional[Callable] = None,
        batch_size: int = 32,
        shuffle: bool = True
):
    """
    统一加载数据集

    :param urls: 文件 URL 列表
    :param framework: "torch" 或 "tf"
    :param decode_fn: bytes -> decoded tensor/function
    :param batch_size: batch 大小
    :param shuffle: 是否打乱
    :return: 可直接迭代的数据集
    """
    if framework == "torch":
        from jcclang.tests.remotefile.jcweaver_dataset import JCWeaverDataset
        from torch.utils.data import DataLoader

        dataset = JCWeaverDataset(urls, transform=decode_fn)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

    elif framework == "tf":
        from jcclang.tests.remotefile.jcweaver_tf_dataset import JCWeaverTFDataset
        import tensorflow as tf

        dataset = JCWeaverTFDataset(urls, decode_fn=decode_fn)
        return dataset.to_tf_dataset(
            batch_size=batch_size,
            output_types=tf.string if decode_fn is None else None,
            output_shapes=()
        )

    else:
        raise ValueError(f"Unsupported framework: {framework}")
