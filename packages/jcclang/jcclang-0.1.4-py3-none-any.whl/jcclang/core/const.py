from enum import Enum

PLATFORM = "platform"
PLATFORM_OPENI = "1865927992266461184"
PLATFORM_MODELARTS = "1790300942428540928"


class DataType:
    DATASET = "dataset"
    MODEL = "model"
    CODE = "code"


class NodeType:
    DATA_RETURN = "DataReturn"
    AI_TRAIN = "AITrain"
    BINDING = "Binding"
    START = "Start"
    END = "End"


class NodeID:
    START_ID = "-1"
    END_ID = "-2"
    FIRST_ID = "1"


class Platform:
    OPENI = "1865927992266461184"
    MODELARTS = "1790300942428540928"
    OCTOPUS = "octopus"


class SourceType(Enum):
    JCS = "JCS"
    LOCAL = "LOCAL"


class JCSAPI:
    PRESIGNED = "/presigned/object/download"
