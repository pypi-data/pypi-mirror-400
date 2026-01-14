from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Generic, TypeVar

TInputs = TypeVar("TInputs")
TOutputs = TypeVar("TOutputs")


class LazyOutputRef:
    def __init__(self, node: "Node", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


class Node(Generic[TInputs, TOutputs]):
    id_counter = 0

    def __init__(self, name: str, description: str):
        Node.id_counter += 1
        self.id = str(Node.id_counter)
        self.name = name
        self.description = description
        self.dependencies: list[str] = []
        self.inputs: TInputs = None  # 子类指定
        self.outputs: TOutputs = None  # 子类指定

    def output(self, key: str) -> LazyOutputRef:
        if not hasattr(self.outputs, key):
            raise AttributeError(f"Invalid output '{key}' for {self.__class__.__name__}")
        return LazyOutputRef(self, key)

    def to_dict(self) -> Dict[str, Any]:
        def serialize(value: Any):
            if isinstance(value, LazyOutputRef):
                # 注册依赖
                if value.node.id not in self.dependencies:
                    self.dependencies.append(value.node.id)
                return value.resolve()
            return value

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "depends_on": self.dependencies,
            "params": {k: serialize(v) for k, v in asdict(self.inputs).items()},
        }


# ---------------- 子类定义 ----------------

@dataclass
class ExtractInputs:
    source: str


@dataclass
class ExtractOutputs:
    raw_data: str


class ExtractNode(Node[ExtractInputs, ExtractOutputs]):
    def __init__(self, name="Extract", description="提取数据"):
        super().__init__(name, description)
        self.inputs = ExtractInputs(source="")
        self.outputs = ExtractOutputs(raw_data="raw_data")


@dataclass
class TransformInputs:
    input: Any  # 可以更严格，比如 `str | LazyOutputRef`


@dataclass
class TransformOutputs:
    cleaned_data: str


class TransformNode(Node[TransformInputs, TransformOutputs]):
    def __init__(self, name="Transform", description="转换数据"):
        super().__init__(name, description)
        self.inputs = TransformInputs(input="")
        self.outputs = TransformOutputs(cleaned_data="cleaned_data")


@dataclass
class LoadInputs:
    input: int


@dataclass
class LoadOutputs:
    result: str


class LoadNode(Node[LoadInputs, LoadOutputs]):
    def __init__(self, name="Load", description="加载数据"):
        super().__init__(name, description)
        self.inputs = LoadInputs(input=0)
        self.outputs = LoadOutputs(result="result")


# ---------------- 使用示例 ----------------

def test_node5():
    extract = ExtractNode()
    transform = TransformNode()
    load = LoadNode()

    # 类型安全：IDE / mypy 会报错如果字段拼错或类型不对
    transform.inputs.input = extract.output("raw_data")
    load.inputs.input = transform.output("cleaned_data")
    load.inputs.input = "1111"

    print(load.to_dict())
