from dataclasses import dataclass

from jcclang.core.const import NodeType
from jcclang.nodes.base_node import Node


@dataclass
class DataReturnInputs:
    package_name: str
    output: str
    platform: str


@dataclass
class DataReturnOutputs:
    package_id: int


class DataReturnNode(Node[DataReturnInputs, DataReturnOutputs]):
    def __init__(self, name="", description="回源"):
        super().__init__(name, NodeType.DATA_RETURN, description)
        self.inputs = DataReturnInputs(package_name="", output="", platform="")
        self.outputs = DataReturnOutputs(package_id=0)
