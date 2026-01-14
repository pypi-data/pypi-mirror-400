from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict, Generic, TypeVar


# 作用是 在类型注解中引入泛型（generic types），让函数、类能支持多种类型，而不仅仅是写死的某个类型。
TInputs = TypeVar("TInputs")
TOutputs = TypeVar("TOutputs")


class OutputRef:
    def __init__(self, node: "Node", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


# 通过 Generic[T] 告诉类型检查器：这个类依赖于一个类型参数 T，Generic[T] 的主要作用是 声明类的类型参数
# TypeVar 定义类型变量。 Generic 让类声明自己支持哪些类型变量。 两者配合，才能写出泛型类，就像 list[T]、dict[K, V] 一样。
class Node(Generic[TInputs, TOutputs]):
    id_counter = 0

    def __init__(self, name: str, description: str):
        Node.id_counter += 1
        self.id = str(Node.id_counter)
        self.name = name
        self.description = description
        self.dependencies: list[str] = []
        self.params: Dict[str, Any] = {}
        self.inputs: TInputs = None  # 子类会填
        self.outputs: TOutputs = None  # 子类会填

    def set_param(self, key: str, value: Any):
        # 类型检查
        if not hasattr(self.inputs, key):
            raise AttributeError(f"Invalid param '{key}' for {self.__class__.__name__}")
        # expected_type = next(f.type for f in fields(self.inputs) if f.name == key)
        # if not isinstance(value, expected_type) and not isinstance(value, LazyOutputRef):
        #     raise TypeError(f"Param '{key}' expects {expected_type}, got {type(value)}")

        self.params[key] = value
        if isinstance(value, OutputRef):
            self.dependencies.append(value.node.id)
        return self

    def output(self, key: str) -> OutputRef:
        if not hasattr(self.outputs, key):
            raise AttributeError(f"Invalid output '{key}' for {self.__class__.__name__}")
        return OutputRef(self, key)

    def to_dict(self) -> Dict[str, Any]:
        def serialize(value: Any):
            if isinstance(value, OutputRef):
                return value.resolve()
            return value

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "depends_on": self.dependencies,
            "params": {k: serialize(v) for k, v in self.params.items()},
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
    input: str


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
    package: str


@dataclass
class LoadOutputs:
    result: str


class LoadNode(Node[LoadInputs, LoadOutputs]):
    def __init__(self, name="Load", description="加载数据"):
        super().__init__(name, description)
        self.inputs = LoadInputs(package="")
        self.outputs = LoadOutputs(result="")


# ---------------- 使用示例 ----------------
def test_node4():
    extract = ExtractNode(name="1111")
    transform = TransformNode()
    load = LoadNode()

    # 类型安全：IDE 提示 input / raw_data / cleaned_data
    transform.set_param("input", extract.output("raw_data"))
    load.set_param("package", transform.output("cleaned_data"))

    print(load.to_dict())
