import os

import torch

from jcclang.api.data_loader.llama_loader import ModelConfig, GPTModel, StreamingSafeTensorsLoader

os.environ["GATEWAY_ADDR"] = "http://101.201.215.196:7893"
os.environ["USER_ID"] = "3"
os.environ["JCS_ADDR"] = "https://121.36.5.116:32200"
os.environ["JCS_AK"] = "XEVUusEUeyWqrBpdobcLrg=="
os.environ["JCS_SK"] = "8EjWjDzjAwtPkF6vl0HgYk0SeDsbxDFE55EDgHGUlJM="

if __name__ == "__main__":
    # 1. 配置模型
    config = ModelConfig(
        vocab_size=32000,
        hidden_size=1024,
        num_layers=24,
        num_heads=16,
        max_seq_len=2048
    )

    # 2. 初始化模型
    model = GPTModel(config)
    model.eval()

    # 3. 加载权重（流式）
    safetensors_file = "model.safetensors"
    loader = StreamingSafeTensorsLoader(safetensors_file, device="cuda")  # 流式加载到 GPU
    loader.load_state_dict(model)

    # 4. 简单推理
    tokenizer = ...  # 你可以使用自定义 tokenizer
    input_ids = tokenizer("Hello world", return_tensors="pt")["input_ids"].to("cuda")
    with torch.no_grad():
        logits = model(input_ids)
    print(logits.shape)  # [batch, seq_len, vocab_size]
