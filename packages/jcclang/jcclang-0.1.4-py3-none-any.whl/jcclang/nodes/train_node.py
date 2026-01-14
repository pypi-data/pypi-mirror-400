from dataclasses import dataclass

from jcclang.core.const import NodeType
from jcclang.nodes.base_node import Node


@dataclass
class AITrainInputs:
    dataset_id: int
    model_id: int
    image_id: int
    code_id: int
    envs: dict
    params: dict

    schedule_strategy: str
    platform: str

    # bootstrap_file: str


@dataclass
class AITrainOutputs:
    output: str
    platform: str


class AITrainNode(Node[AITrainInputs, AITrainOutputs]):
    def __init__(self, name="", description="智算训练任务"):
        super().__init__(name, NodeType.AI_TRAIN, description)
        self.inputs = AITrainInputs(dataset_id=0, model_id=0, image_id=0, code_id=0, platform="",
                                    schedule_strategy="", envs={}, params={})
        self.outputs = AITrainOutputs(output="", platform="")
