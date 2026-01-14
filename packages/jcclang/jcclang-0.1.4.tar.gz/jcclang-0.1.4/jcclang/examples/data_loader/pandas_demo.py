# import pandas as pd
import os
import time

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from torch.utils.data import Dataset, DataLoader

from jcclang.api.data_loader.pandas_loader import Pandas
from jcclang.core.const import SourceType
from jcclang.core.model import Source

start_time = time.time()

os.environ["SERVER_URL"] = "http://101.201.215.196:7893"
os.environ["USER_ID"] = "3"
# =====================
# 1. 加载数据
# =====================
# df = pd.read_csv('D:\\Model\\dataset\\UNSW_NB15\\UNSW_NB15_training-set.csv')
pd = Pandas(source=Source(object_id=33184, type=SourceType.JCS))
# pd = Pandas(source=Source(path='D:\\Model\\dataset\\UNSW_NB15\\UNSW_NB15_training-set.csv', type=SourceType.LOCAL))
df = pd.read_csv()
# =====================
# 2. 特征选择
# =====================
features = [
    'dur', 'proto', 'service', 'state', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'rate', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'sinpkt', 'dinpkt',
    'sjit', 'djit', 'swin', 'stcpb', 'dtcpb', 'dwin', 'tcprtt', 'synack', 'ackdat',
    'smean', 'dmean', 'trans_depth', 'response_body_len', 'ct_srv_src', 'ct_state_ttl',
    'ct_dst_ltm', 'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm',
    'is_ftp_login', 'ct_ftp_cmd', 'ct_flw_http_mthd', 'ct_src_ltm', 'ct_srv_dst',
    'is_sm_ips_ports'
]

# 处理类别型特征：LabelEncoder
categorical_cols = ['proto', 'service', 'state']
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))  # 确保都是字符串

# 特征矩阵
X = df[features].values

# 标签：二分类 0 = 正常, 1 = 攻击
y = (df['attack_cat'] != 'Normal').astype(int).values

# =====================
# 3. 数据预处理
# =====================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# 转换为 PyTorch 张量
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)


# =====================
# 4. 自定义 Dataset
# =====================
class NIDS_Dataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


train_dataset = NIDS_Dataset(X_train_tensor, y_train_tensor)
test_dataset = NIDS_Dataset(X_test_tensor, y_test_tensor)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


# =====================
# 5. 定义模型
# =====================
class MLP_NIDS(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(MLP_NIDS, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


input_dim = X_train.shape[1]
hidden_dim = 128
output_dim = 2  # 二分类
model = MLP_NIDS(input_dim, hidden_dim, output_dim)

# 使用 GPU（如果可用）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# =====================
# 6. 损失函数和优化器
# =====================
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

if __name__ == '__main__':
    print(f'Spend time: {time.time() - start_time:.2f}s')

    # =====================
    # 7. 训练循环
    # =====================
    epochs = 1
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {running_loss / len(train_loader):.4f}')

    # =====================
    # 8. 测试与评估
    # =====================
    model.eval()
    y_pred = []
    y_true = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            y_pred.extend(predicted.cpu().numpy())
            y_true.extend(labels.cpu().numpy())

    accuracy = accuracy_score(y_true, y_pred)
    print(f'Test Accuracy: {accuracy * 100:.2f}%')
