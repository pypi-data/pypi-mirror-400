import os

import torch
import transformers.models.auto.configuration_auto as config_auto
import transformers.models.auto.modeling_auto as modeling_auto
import transformers.models.auto.tokenization_auto as token_auto
import transformers.utils
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from transformers import Qwen3ForCausalLM

from jcclang.api.data_loader.transformers_hook.virtual_file_io import virtual_cached_file
from jcclang.core.model import Sources, VirtualFileParams


os.environ["GATEWAY_ADDR"] = "http://101.201.215.196:7893"
os.environ["USER_ID"] = "3"
os.environ["JCS_ADDR"] = "https://121.36.5.116:32200"
os.environ["JCS_AK"] = "XEVUusEUeyWqrBpdobcLrg=="
os.environ["JCS_SK"] = "8EjWjDzjAwtPkF6vl0HgYk0SeDsbxDFE55EDgHGUlJM="

# 假设 sources 列表已经包含 config.json、vocab.json、merges.txt、pytorch_model.bin
sources = Sources.from_dict_list([
    {"path": "tokenizer_config.json", "object_id": 33199, "type": "JCS"},
    {"path": "tokenizer.json", "object_id": 33198, "type": "JCS"},
    {"path": "generation_config.json", "object_id": 33197, "type": "JCS"},
    {"path": "configuration.json", "object_id": 33196, "type": "JCS"},
    {"path": "config.json", "object_id": 33195, "type": "JCS"},
    {"path": "vocab.json", "object_id": 33200, "type": "JCS"},
    {"path": "model.safetensors", "object_id": 33188, "type": "JCS"}
])

vparams = VirtualFileParams()

# monkey patch transformers.cached_file

transformers.utils.cached_file = virtual_cached_file
transformers.utils.hub.cached_file = virtual_cached_file
transformers.utils.generic.cached_file = virtual_cached_file
token_auto.cached_file = virtual_cached_file
config_auto.cached_file = virtual_cached_file
modeling_auto.cached_file = virtual_cached_file

config = AutoConfig.from_pretrained(pretrained_model_name_or_path="D:\\Model\\Qwen3-0.6B-Base", local_files_only=True)
print("model_type:")
print(config.model_type)

tokenizer = AutoTokenizer.from_pretrained(
    "./virtual_model",
    sources=sources,
    vparams=vparams,
    local_files_only=True,  # 🚀 必须加！
    # config=config,
)

model = AutoModelForCausalLM.from_pretrained(
    "./virtual_model",
    sources=sources,
    vparams=vparams,
    local_files_only=True,  # 🚀 必须加！
    # config=config,
)

if __name__ == '__main__':
    # 编码输入
    input_text = "请介绍一下人工智能。"
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    # 生成文本
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

    # 解码输出
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(output_text)
