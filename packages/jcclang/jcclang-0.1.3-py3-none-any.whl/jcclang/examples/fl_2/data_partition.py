import os
import pickle

from torchvision import datasets, transforms


def partition_mnist(num_clients: int = 3, shards_per_client: int = 2):
    """
    将 MNIST 划分为 num_clients * shards_per_client 个 shard，
    每个客户端分配 shards_per_client 个 shard（可重叠或不重叠）
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    dataset = datasets.MNIST(root=f'D:\\Model\\dataset\\mnist_fl', train=True, download=False, transform=transform)

    # 按标签排序（便于 Non-IID 划分）
    sorted_indices = sorted(range(len(dataset)), key=lambda i: dataset.targets[i].item())

    # 切分为 shards
    total_shards = num_clients * shards_per_client
    shard_size = len(sorted_indices) // total_shards
    shards = []
    for i in range(total_shards):
        start = i * shard_size
        end = start + shard_size if i < total_shards - 1 else len(sorted_indices)
        shards.append(sorted_indices[start:end])

    # 分配给客户端
    client_data = {}
    for client_id in range(num_clients):
        client_shards = []
        for j in range(shards_per_client):
            shard_idx = client_id * shards_per_client + j
            client_shards.extend(shards[shard_idx])
        client_data[f"client_{client_id}"] = client_shards

    # 保存每个客户端的数据索引
    os.makedirs("client_data", exist_ok=True)
    for client_id, indices in client_data.items():
        with open(f"client_data/{client_id}.pkl", "wb") as f:
            pickle.dump(indices, f)

    print(f"Partitioned MNIST into {num_clients} clients, each with {shards_per_client} shards.")


if __name__ == "__main__":
    partition_mnist(num_clients=5, shards_per_client=2)
