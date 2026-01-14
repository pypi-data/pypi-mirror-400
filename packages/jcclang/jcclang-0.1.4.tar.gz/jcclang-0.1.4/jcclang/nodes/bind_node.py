from dataclasses import dataclass

from jcclang.core.const import NodeType
from jcclang.nodes.base_node import Node


@dataclass
class DatasetBindInputs:
    platforms: list[str]
    category: str
    package_id: int
    output: str


@dataclass
class DatasetBindOutputs:
    bind_id: int


class DatasetBindNode(Node[DatasetBindInputs, DatasetBindOutputs]):
    def __init__(self, name="", description="创建数据集"):
        super().__init__(name, NodeType.BINDING, description)
        self.inputs = DatasetBindInputs(platforms=[], category="", package_id=0, output="")
        self.outputs = DatasetBindOutputs(bind_id=0)
