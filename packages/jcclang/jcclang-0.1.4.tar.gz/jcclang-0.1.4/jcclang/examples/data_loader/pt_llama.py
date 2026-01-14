from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import torch


config = AutoConfig.from_pretrained("D:\\Model\\Qwen3-0.6B-Base")
print("model config:")
print(config.model_type)

# 加载模型
tokenizer = AutoTokenizer.from_pretrained("D:\\Model\\Qwen3-0.6B-Base")
model = AutoModelForCausalLM.from_pretrained(
    "D:\\Model\\Qwen3-0.6B-Base",
    torch_dtype=torch.bfloat16,
    device_map="auto"
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
