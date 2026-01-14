import os
import pickle
from typing import Tuple, List

import torch
from torchvision import datasets, transforms
from torch.utils.data import TensorDataset


def partition_mnist_save_raw_data(
        num_clients: int = 3,
        shards_per_client: int = 2,
        data_root: str = r'D:\Model\dataset\mnist_fl',
        output_dir: str = "client_data_raw"
):
    """
    将 MNIST 划分为客户端专属的 (images, labels) 数据块，并保存为 .pkl 文件。
    每个文件包含：
        {
            'images': torch.Tensor [N, 1, 28, 28],
            'labels': torch.Tensor [N]
        }
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    # 加载完整训练集
    dataset = datasets.MNIST(root=data_root, train=True, download=False, transform=transform)

    # 按标签排序（便于 Non-IID）
    sorted_indices = sorted(range(len(dataset)), key=lambda i: dataset.targets[i].item())

    # 切分为 shards
    total_shards = num_clients * shards_per_client
    shard_size = len(sorted_indices) // total_shards
    shards = []
    for i in range(total_shards):
        start = i * shard_size
        end = start + shard_size if i < total_shards - 1 else len(sorted_indices)
        shards.append(sorted_indices[start:end])

    # 为每个客户端收集数据
    os.makedirs(output_dir, exist_ok=True)

    for client_id in range(num_clients):
        client_indices = []
        for j in range(shards_per_client):
            shard_idx = client_id * shards_per_client + j
            client_indices.extend(shards[shard_idx])

        # 提取 images 和 labels
        images = []
        labels = []
        for idx in client_indices:
            img, label = dataset[idx]  # img 已经是归一化后的 tensor
            images.append(img)
            labels.append(label)

        # 转为 tensor
        images_tensor = torch.stack(images)      # [N, 1, 28, 28]
        labels_tensor = torch.tensor(labels)     # [N]

        # 保存
        client_data = {
            'images': images_tensor,
            'labels': labels_tensor,
            'num_samples': len(labels_tensor)
        }

        filepath = os.path.join(output_dir, f"block_{client_id}.pkl")
        with open(filepath, "wb") as f:
            pickle.dump(client_data, f)

        print(f"Saved client_{client_id}: {len(labels)} samples to {filepath}")

    print(f"\nPartitioned MNIST into {num_clients} clients. "
          f"Each has {shards_per_client} shards. Data saved in '{output_dir}'.")


# 使用示例
if __name__ == "__main__":
    partition_mnist_save_raw_data(num_clients=3, shards_per_client=2)