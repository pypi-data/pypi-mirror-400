import gzip
import io
import os
import time

import numpy as np
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, datasets

from jcclang.core.logger import jcwLogger

start_time = time.time()
os.environ["SERVER_URL"] = "http://101.201.215.196:7893"
os.environ["USER_ID"] = "3"

presign_url = f"http://101.201.215.196:7893/storage/presign"
params = {
    "objectID": 143,
}

json_params = {
    "userID": 3,
    "info": {
        "type": "download",
        "params": params
    }
}
session = requests.Session()
resp = session.post(presign_url, json=json_params, stream=True)
data = resp.json()
presign_url = str(data.get("data").get("presignUrl"))
resp2 = session.get(presign_url, stream=True, verify=False)
# 将resp2.content写入到文件中
data_path = 'D:\\Model\\dataset\\mnist\\MNIST\\raw\\train_data01'
with open(data_path, 'wb') as f:
    for chunk in resp2.iter_content(chunk_size=64 * 1024):
        if chunk:
            f.write(chunk)

# =====================
# 1. 超参数
# =====================
batch_size = 64
learning_rate = 0.001
epochs = 2
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =====================
# 2. 数据加载
# =====================
transform = transforms.Compose([
    transforms.ToTensor(),  # 转为Tensor
    transforms.Normalize((0.1307,), (0.3081,))  # 标准化
])

# def decode_image(raw):
#     """
#     raw: (image_bytes, label) tuple
#     - image_bytes: 784 bytes (28x28)
#     - label: int
#     """
#     image_bytes, label = raw
#     image = np.frombuffer(image_bytes, dtype=np.uint8).reshape(28, 28)
#     image = Image.fromarray(image, mode='L')
#     return image, label


# 缓存每个 raw 文件解码后的图片
decoded_cache = {}


def decode_image(raw: bytes):
    """
    将 gzip MNIST 原始数据解码为 numpy ndarray，返回 shape [H, W]。
    DataLoader 会在 __getitem__ 中对单个样本调用 transform。
    """
    key = id(raw)
    if key not in decoded_cache:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:
            magic = int.from_bytes(f.read(4), 'big')
            n_images = int.from_bytes(f.read(4), 'big')
            n_rows = int.from_bytes(f.read(4), 'big')
            n_cols = int.from_bytes(f.read(4), 'big')

            data1 = f.read(n_images * n_rows * n_cols)
            images1 = np.frombuffer(data1, dtype=np.uint8).reshape(n_images, n_rows, n_cols)

            # 缓存每张图片
            decoded_cache[key] = images1
    # 取第 0 张图片（Dataset 会根据索引取对应样本）
    # 返回 shape [H, W]，不加通道，保持 ndarray
    return decoded_cache[key][0]


# =====================
# 3. 定义网络
# =====================
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        # 经过 conv1 + conv2 后尺寸为 64 × 24 × 24 = 36864
        self.fc1 = nn.Linear(36864, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))  # -> [B, 32, 26, 26]
        x = torch.relu(self.conv2(x))  # -> [B, 64, 24, 24]
        x = torch.flatten(x, 1)  # -> [B, 36864]
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


model = CNN().to(device)

# =====================
# 4. 定义损失和优化器
# =====================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

if __name__ == '__main__':

    # def test_pt_mnist():
    jcwLogger.debug("Starting training...")

    train_dataset = datasets.MNIST(root=data_path)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, num_workers=4, shuffle=True)

    # =====================
    # 5. 训练循环
    # =====================
    for epoch in range(epochs):
        jcwLogger.info(f"Epoch [{epoch + 1}/{epochs}]")
        model.train()
        total_loss = 0
        for batch_idx, (images, target) in enumerate(train_loader):
            images, target = images.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(images)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{epochs}] - Loss: {avg_loss:.4f}")

    jcwLogger.info(f"Training completed in {time.time() - start_time:.2f} seconds.")
    # =====================
    # 6. 测试模型
    # =====================
    # model.eval()
    # correct = 0
    # total = 0
    #
    # test_dataset = Dataset(
    #     sources=Sources.from_dict_list(
    #         [
    #             {"object_id": 152, "label": 0},
    #         ]
    #     ),
    #     decoder=decode_image,
    #     transform=transform
    # )
    # test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    #
    # with torch.no_grad():
    #     for images, target in test_loader:
    #         images, target = images.to(device), target.to(device)
    #         outputs = model(images)
    #         _, predicted = torch.max(outputs.data, 1)
    #         total += target.size(0)
    #         correct += (predicted == target).sum().item()
    #
    # accuracy = 100 * correct / total
    # print(f"Test Accuracy: {accuracy:.2f}%")

    # =====================
    # 7. 保存模型
    # =====================
    # torch.save(model.state_dict(), "mnist_cnn.pth")
    # print("模型已保存到 mnist_cnn.pth")
