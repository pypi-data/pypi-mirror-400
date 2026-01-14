from typing import List, Dict, Any

import torch
import torch.nn as nn

from jcclang.examples.fl_3.utils import logger


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = torch.relu(x)
        x = self.conv2(x)
        x = torch.relu(x)
        x = torch.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = torch.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)


def serialize_model(model) -> bytes:
    import torch
    from io import BytesIO
    buffer = BytesIO()
    torch.save(model.state_dict(), buffer)
    return buffer.getvalue()


def deserialize_model(model_bytes) -> Any:
    import torch
    from io import BytesIO
    buffer = BytesIO(model_bytes)
    state_dict = torch.load(buffer, map_location='cpu')
    logger.info("[Leader] Deserializing model succeed")
    # 注意：此处需有模型结构！实际中可传入模板
    # 本设计假设 Leader 持有 model_template，此处应返回完整模型
    # 为简化，aggregate_models 直接操作 state_dict
    return state_dict


def aggregate_models(local_state_dicts: List[Dict], weights: List[int], global_model):
    """在 global_model 上原地聚合"""
    import torch
    total_weight = sum(weights)
    if total_weight == 0:
        logger.warning("[Leader] No weights provided")
        total_weight = 1

    # 初始化为加权平均
    averaged_state = {}
    for key in global_model.state_dict().keys():
        averaged_state[key] = torch.zeros_like(global_model.state_dict()[key], dtype=torch.float32)
        for i, local_sd in enumerate(local_state_dicts):
            averaged_state[key] += (weights[i] / total_weight) * local_sd[key].float()
        averaged_state[key] = averaged_state[key].type_as(global_model.state_dict()[key])

    global_model.load_state_dict(averaged_state)
    return global_model
