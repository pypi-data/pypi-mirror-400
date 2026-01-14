import tensorflow as tf


def test_tf_demo():
    # 1. 加载数据集
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    # 2. 数据预处理
    x_train = x_train.astype("float32") / 255.0  # 归一化到 [0,1]
    x_test = x_test.astype("float32") / 255.0

    # 3. 构建 tf.data.Dataset
    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(10000).batch(32)  # 打乱并分批

    # 4. 打印一批看看
    for images, labels in train_ds.take(1):
        print("图像批次形状:", images.shape)
        print("标签批次形状:", labels.shape)
