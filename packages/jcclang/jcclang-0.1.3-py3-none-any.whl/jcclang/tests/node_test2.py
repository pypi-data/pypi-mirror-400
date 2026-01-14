from typing import Any, Dict, TypeVar, Generic, TypedDict, get_type_hints


# ------------------------------
# 懒引用
# ------------------------------
class LazyOutputRef:
    def __init__(self, node: "BaseNode", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


# ------------------------------
# 输入 / 输出 Schema 示例
# ------------------------------
class ExtractInputs(TypedDict, total=False):
    url: str


class ExtractOutputs(TypedDict, total=False):
    raw_data: str


class TransformInputs(TypedDict, total=False):
    input: str  # 引用 ExtractOutputs["raw_data"]


class TransformOutputs(TypedDict, total=False):
    cleaned_data: str


class LoadInputs(TypedDict, total=False):
    input: str  # 引用 TransformOutputs["cleaned_data"]


class LoadOutputs(TypedDict, total=False):
    status: str


# ------------------------------
# Node 基类
# ------------------------------
InputSchema = TypeVar("InputSchema", bound=TypedDict)
OutputSchema = TypeVar("OutputSchema", bound=TypedDict)


class BaseNode(Generic[InputSchema, OutputSchema]):
    _id_counter = 0

    def __init__(self, name: str, description: str):
        BaseNode._id_counter += 1
        self.id = f"node_{BaseNode._id_counter}"
        self.name = name
        self.description = description
        self.params: Dict[str, Any] = {}
        self.dependencies: list[str] = []

    # 类型安全的输入参数
    def set_param(self, key: str, value: Any):
        hints = get_type_hints(self.__class__.Inputs)  # 获取输入类型提示
        if key not in hints:
            raise KeyError(f"Invalid input key '{key}' for node {self.__class__.__name__}")
        self.params[key] = value
        if isinstance(value, LazyOutputRef):
            self.dependencies.append(value.node.id)
        return self

    # 类型安全的输出引用
    def output(self, key: str) -> LazyOutputRef:
        hints = get_type_hints(self.__class__.Outputs)  # 获取输出类型提示
        if key not in hints:
            raise KeyError(f"Invalid output key '{key}' for node {self.__class__.__name__}")
        return LazyOutputRef(self, key)

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


# ------------------------------
# 子类节点定义
# ------------------------------
class ExtractNode(BaseNode[ExtractInputs, ExtractOutputs]):
    class Inputs(ExtractInputs): ...

    class Outputs(ExtractOutputs): ...


class TransformNode(BaseNode[TransformInputs, TransformOutputs]):
    class Inputs(TransformInputs): ...

    class Outputs(TransformOutputs): ...


class LoadNode(BaseNode[LoadInputs, LoadOutputs]):
    class Inputs(LoadInputs): ...

    class Outputs(LoadOutputs): ...


# ------------------------------
# 使用示例
# ------------------------------
extract = ExtractNode(name="Extract", description="提取数据")
transform = TransformNode(name="Transform", description="转换数据")
load = LoadNode(name="Load", description="加载数据")

# 输入输出都是类型安全的
extract.set_param("url", "http://example.com/data")
transform.set_param("input", extract.output("raw_data"))
load.set_param("input", transform.output("cleaned_data"))

# 导出 IR
print(load.to_dict())
