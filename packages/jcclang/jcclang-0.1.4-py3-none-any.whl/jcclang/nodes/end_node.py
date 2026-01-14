from dataclasses import dataclass

from jcclang.core.const import NodeType
from jcclang.nodes.base_node import Node


@dataclass
class EndInputs:
    pass


@dataclass
class EndOutputs:
    pass


class EndNode(Node[EndInputs, EndOutputs]):
    def __init__(self, name="", description="end node"):
        super().__init__(name, NodeType.END, description)
        self.inputs = EndInputs()
        self.outputs = EndOutputs()
