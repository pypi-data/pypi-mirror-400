import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms

from jcclang.api.data_loader.torch_loader import Dataset
from jcclang.core.logger import jcwLogger
from jcclang.core.model import Sources

start_time = time.time()
os.environ["SERVER_URL"] = "http://101.201.215.196:7893"
os.environ["USER_ID"] = "3"

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


def decode_image(raw):
    """
    raw: (image_bytes, label) tuple
    - image_bytes: 784 bytes (28x28)
    - label: int
    """
    image_bytes, label = raw
    image = np.frombuffer(image_bytes, dtype=np.uint8).reshape(28, 28)
    image = Image.fromarray(image, mode='L')
    return image, label


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

    train_dataset = Dataset(
        sources=Sources.from_dict_list(
            [
                {"object_id": 33185, "label": 0},
            ]
        ),
        decoder=decode_image,
        transform=transform
    )

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
