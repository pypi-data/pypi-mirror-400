import os
import torch
import torch.nn as nn
from safetensors.torch import safe_open

# ============================
# 1️⃣ 模型配置类
# ============================

class ModelConfig:
    """
    简单配置类，描述模型结构
    """
    def __init__(self, vocab_size, hidden_size, num_layers, num_heads, max_seq_len):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_seq_len = max_seq_len

# ============================
# 2️⃣ 自定义模型类
# ============================

class GPTLayer(nn.Module):
    def __init__(self, hidden_size, num_heads):
        super().__init__()
        self.attn = nn.MultiheadAttention(embed_dim=hidden_size, num_heads=num_heads, batch_first=True)
        self.ffn = nn.Sequential(
            nn.Linear(hidden_size, 4 * hidden_size),
            nn.GELU(),
            nn.Linear(4 * hidden_size, hidden_size)
        )
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)

    def forward(self, x):
        attn_out, _ = self.attn(x, x, x)
        x = self.ln1(x + attn_out)
        x = self.ln2(x + self.ffn(x))
        return x

class GPTModel(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([GPTLayer(config.hidden_size, config.num_heads)
                                     for _ in range(config.num_layers)])
        self.ln_f = nn.LayerNorm(config.hidden_size)
        self.head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

    def forward(self, input_ids):
        x = self.embed_tokens(input_ids)
        for layer in self.layers:
            x = layer(x)
        x = self.ln_f(x)
        logits = self.head(x)
        return logits

# ============================
# 3️⃣ 流式 Safetensors 权重加载器
# ============================

class StreamingSafeTensorsLoader:
    """
    支持按需加载 safetensors 权重到 CPU/GPU
    """
    def __init__(self, filename: str, device="cpu"):
        self.filename = filename
        self.device = device
        self._file = safe_open(filename, framework="pt")
        self.keys = self._file.keys()

    def load_tensor(self, name: str, device=None):
        """按需加载单个 tensor"""
        dev = device or self.device
        tensor = self._file.get_tensor(name).to(dev)
        return tensor

    def load_state_dict(self, model: nn.Module, device=None):
        """
        按 tensor 名称加载权重到模型
        支持流式加载：可选择只加载部分层
        """
        dev = device or self.device
        state_dict = {}
        for name, param in model.named_parameters():
            if name in self.keys:
                tensor = self._file.get_tensor(name).to(dev)
                state_dict[name] = tensor
            else:
                print(f"[Warning] weight {name} not found in safetensors")
        model.load_state_dict(state_dict, strict=False)

# ============================
# 4️⃣ 使用示例
# ============================

