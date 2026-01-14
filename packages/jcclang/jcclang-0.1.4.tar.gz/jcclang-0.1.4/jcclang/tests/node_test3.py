from typing import Any, Dict, Generic, TypeVar


# -----------------------------------------
# Lazy 引用
# -----------------------------------------
class LazyOutputRef:
    def __init__(self, node: "Node", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


# -----------------------------------------
# 类型安全的 Output 容器
# -----------------------------------------
class TypedOutputs:
    """基类，不存数据，只存 schema 信息"""

    def __init__(self, node: "Node"):
        self._node = node
        # 自动把类字段暴露为 LazyOutputRef
        for name in self.__annotations__:
            setattr(self, name, LazyOutputRef(node, name))


# -----------------------------------------
# 泛型 Node
# -----------------------------------------
TOutputs = TypeVar("TOutputs", bound=TypedOutputs)


class Node(Generic[TOutputs]):
    _id_counter = 0

    def __init__(self, name: str, description: str, outputs_cls: type[TOutputs]):
        Node._id_counter += 1
        self.id = f"node_{Node._id_counter}"
        self.name = name
        self.description = description
        self.dependencies: list[str] = []
        self.params: Dict[str, Any] = {}

        # 绑定输出 schema
        self.output: TOutputs = outputs_cls(self)

    def set_param(self, key: str, value: Any):
        self.params[key] = value
        if isinstance(value, LazyOutputRef):
            self.dependencies.append(value.node.id)
        return self

    def to_dict(self) -> Dict[str, Any]:
        def serialize(value: Any):
            if isinstance(value, LazyOutputRef):
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


# -----------------------------------------
# 定义具体 Node 输出 Schema
# -----------------------------------------
class ExtractOutputs(TypedOutputs):
    raw_data: str
    meta: dict


class TransformOutputs(TypedOutputs):
    cleaned_data: str
    stats: dict


class LoadOutputs(TypedOutputs):
    success: bool


# -----------------------------------------
# 使用示例
# -----------------------------------------
extract = Node(name="Extract", description="提取数据", outputs_cls=ExtractOutputs)
transform = Node(name="Transform", description="转换数据", outputs_cls=TransformOutputs)
load = Node(name="Load", description="加载数据", outputs_cls=LoadOutputs)

# 类型安全参数设置（IDE 会提示 output.raw_data / output.meta）
transform.set_param("input", extract.output.raw_data)
load.set_param("input", transform.output.cleaned_data)
load.set_param("output", transform.output.stats)

# 导出 IR
print(load.to_dict())
