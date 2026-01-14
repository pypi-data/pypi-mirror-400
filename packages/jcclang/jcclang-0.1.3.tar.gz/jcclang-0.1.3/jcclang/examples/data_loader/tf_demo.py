import tensorflow as tf

from jcclang.api.data_loader.tensorflow_loader import Dataset
from jcclang.core.model import Sources


def decode_image(raw_bytes):
    import numpy as np
    import gzip
    import io

    with gzip.GzipFile(fileobj=io.BytesIO(raw_bytes)) as f:
        n_images = int.from_bytes(f.read(4), 'big')
        n_rows = int.from_bytes(f.read(4), 'big')
        n_cols = int.from_bytes(f.read(4), 'big')
        data = f.read(n_images * n_rows * n_cols)
        images = np.frombuffer(data, dtype=np.uint8).reshape(n_images, n_rows, n_cols)
        return images


sources = Sources.from_dict_list([{"object_id": 143, "label": 0}])
dataset_tf = Dataset(sources, decoder=decode_image)
tf_dataset = dataset_tf.to_tf_dataset(output_types=tf.float32, output_shapes=(28, 28), batch_size=64)

if __name__ == '__main__':
    for batch_images, batch_labels in tf_dataset:
        print(batch_images.shape, batch_labels.shape)
