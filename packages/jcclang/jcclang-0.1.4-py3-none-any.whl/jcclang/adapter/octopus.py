import os

from jcclang.adapter.base_adapter import BaseAdapter
from jcclang.core.const import DataType
from jcclang.core.logger import jcwLogger


class OctopusAdapter(BaseAdapter):
    def __init__(self):
        self.output = ""

    def before_task(self, inputs, context: dict):
        jcwLogger.info("execute before task")

    def after_task(self, outputs, context: dict):
        jcwLogger.info("execute after task")

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            data_path = os.environ.get("dataset_input")
            if not data_path:
                jcwLogger.error("dataset_input is not set")
                return ""
            return os.path.join(data_path, file_path)

        if data_type == DataType.MODEL:
            data_path = os.environ.get("model_input")
            if not data_path:
                jcwLogger.error("model_input is not set")
                return ""
            return os.path.join(data_path, file_path)

        if data_type == DataType.CODE:
            data_path = os.environ.get("code_input")
            if not data_path:
                jcwLogger.error("code_input is not set")
                return ""
            return os.path.join(data_path, file_path)
        jcwLogger.error(f"Unknown data type for input: {data_type}")
        return ""

    def output_prepare(self, data_type: str, file_path: str):
        data_path = os.environ.get("output",  "./output")

        if not os.path.exists(data_path):
            jcwLogger.info(f"create output directory: {data_path}")
            os.makedirs(data_path)

        return os.path.join(data_path, file_path)
