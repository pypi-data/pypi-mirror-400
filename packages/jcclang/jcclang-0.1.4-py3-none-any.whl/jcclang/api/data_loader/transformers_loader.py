import json

import torch
from transformers import PreTrainedTokenizerFast, AutoModelForCausalLM

from jcclang.core.model import Source
from jcclang.virtualfile.virtual_file import VirtualFile, VirtualFileParams


# =========================
# 1️⃣ Tokenizer from JCWeaver
# =========================
class JCWeaverTokenizer(PreTrainedTokenizerFast):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str, *args, **kwargs):
        """
        支持：
            - pretrained_model_name_or_path: 可以是本地路径（兼容原接口）
            - kwargs['source']: JCWeaver Source 对象
            - kwargs['vf_params']: VirtualFileParams
        """
        source = kwargs.pop("source", None)
        vf_params = kwargs.pop("vf_params", None)

        if source is not None:
            vf_params = vf_params or VirtualFileParams()
            vf = VirtualFile(source, vf_params)
            raw_bytes = vf.read()
            vf.close()
            tokenizer_json = raw_bytes.decode("utf-8")
            return cls.from_str(tokenizer_json)

        # 否则走原生逻辑
        return super().from_pretrained(pretrained_model_name_or_path, *args, **kwargs)


# =========================
# 2️⃣ Model from JCWeaver
# =========================
class JCWeaverModel(AutoModelForCausalLM):
    @classmethod
    def from_pretrained(cls, source: Source, vf_params: VirtualFileParams = None, **kwargs):
        """
        source: Source对象（JCS 或本地）
        kwargs: 可以传递 torch_dtype, device_map 等
        """
        vf_params = vf_params or VirtualFileParams()
        vf = VirtualFile(source, vf_params)

        # 1) 读取配置文件
        # 假设 source.path 对应模型目录，里面有 config.json 和 pytorch_model.bin
        # 这里我们用 VirtualFile 读取
        config_path = f"{source.path}/config.json"
        model_path = f"{source.path}/pytorch_model.bin"

        # 读取 config.json
        config_vf = VirtualFile(Source(path=config_path, object_id=source.object_id, type=source.type), vf_params)
        config_bytes = config_vf.read()
        config_vf.close()
        config_dict = json.loads(config_bytes.decode("utf-8"))

        # 2) 构建模型实例
        model = cls.from_config_dict(config_dict)

        # 3) 读取权重
        model_vf = VirtualFile(Source(path=model_path, object_id=source.object_id, type=source.type), vf_params)
        state_bytes = model_vf.read()
        model_vf.close()
        # 加载 state_dict
        import io
        state_dict = torch.load(io.BytesIO(state_bytes), map_location="cpu")
        model.load_state_dict(state_dict)

        # 4) 可选 device/dtype
        if "device_map" in kwargs or "torch_dtype" in kwargs:
            device_map = kwargs.get("device_map", None)
            torch_dtype = kwargs.get("torch_dtype", None)
            if torch_dtype:
                model = model.to(torch_dtype)
            if device_map:
                model = model.to(device_map)

        return model


# =========================
# 3️⃣ 使用示例
# =========================
if __name__ == "__main__":
    vf_params = VirtualFileParams(block_size=8 * 1024 * 1024, mem_cache_bytes=2 * 1024 * 1024 * 1024)

    # Tokenizer
    tokenizer_source = Source(path="D:/Model/Qwen3-0.6B-Base/tokenizer.json", object_id=1234, type=SourceType.JCS)
    tokenizer = JCWeaverTokenizer.from_pretrained(tokenizer_source, vf_params)

    # Model
    model_source = Source(path="D:/Model/Qwen3-0.6B-Base", object_id=1234, type=SourceType.JCS)
    model = JCWeaverModel.from_pretrained(model_source, vf_params, torch_dtype=torch.bfloat16, device_map="auto")

    # 推理示例
    prompt = "Hello, JCWeaver!"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
