import os
import struct

import numpy as np
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms

# 假设从 jcclang 导入你的 Dataset 定义
from jcclang.core.model import Sources, Source


# ==============================
# 2. 定义 EMNIST Decoder
# ==============================
def emnist_decoder(raw):
    """
    raw: (image_bytes, label) tuple
    - image_bytes: 784 bytes (28x28)
    - label: int
    """
    image_bytes, label = raw
    image = np.frombuffer(image_bytes, dtype=np.uint8).reshape(28, 28)
    image = Image.fromarray(image, mode='L')
    return image, label


# ==============================
# 3. 从 IDX 文件构造 Sources
# ==============================
def load_emnist_sources(image_path, label_path):
    with open(image_path, 'rb') as f:
        magic, num_images, rows, cols = struct.unpack('>IIII', f.read(16))
        image_data = np.frombuffer(f.read(), dtype=np.uint8).reshape(num_images, rows * cols)

    with open(label_path, 'rb') as f:
        magic, num_labels = struct.unpack('>II', f.read(8))
        labels = np.frombuffer(f.read(), dtype=np.uint8)

    assert len(image_data) == len(labels), "图像与标签数量不匹配！"

    items = []
    for i in range(len(labels)):
        # 每个 Source 可以包含路径、元数据、标签等
        # 这里我们模拟一个虚拟文件 info
        info = Source(path=f"emnist-{i}", label=int(labels[i]))
        info.data = (image_data[i].tobytes(), int(labels[i]))  # 存到虚拟结构
        items.append(info)

    return Sources(items=items)


# ==============================
# 4. 模拟 VirtualFile（无需真实文件）
# ==============================
class VirtualFile:
    def __init__(self, info, params=None):
        self.info = info

    def read(self):
        # 直接返回 Source 中缓存的数据
        return self.info.data

    def close(self):
        pass


# ==============================
# 5. 测试加载流程
# ==============================
if __name__ == "__main__":
    data_root = "./data/emnist"
    train_images = os.path.join(data_root, "emnist-byclass-train-images-idx3-ubyte")
    train_labels = os.path.join(data_root, "emnist-byclass-train-labels-idx1-ubyte")

    print("⏳ 正在加载 EMNIST 源...")
    sources = load_emnist_sources(train_images, train_labels)
    print(f"✅ 已加载 {len(sources.items)} 条样本")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = Dataset(
        sources=sources,
        transform=lambda sample: (transform(sample[0]), sample[1]),  # transform 只处理图像
        decoder=emnist_decoder
    )

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

    # 测试取一个 batch
    images, labels = next(iter(train_loader))
    print(f"图像 shape: {images.shape}, 标签示例: {labels[:10]}")
