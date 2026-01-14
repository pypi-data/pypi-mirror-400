import argparse
import os

from jcclang.adapter.base_adapter import BaseAdapter
from jcclang.core.const import DataType
from jcclang.core.logger import jcwLogger


class OpenIAdapter(BaseAdapter):
    def __init__(self):
        from c2net.context import prepare, upload_output
        self._prepare = prepare()
        self._upload_output = upload_output
        self.output = ""
        self.parser = argparse.ArgumentParser(description='Model Training with input parameter')

    def before_task(self, inputs, context: dict):
        jcwLogger.info("execute before task")
        pass

    def after_task(self, outputs, context: dict):
        jcwLogger.info("execute after task")
        self._upload_output()

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            self.parser.add_argument('--dataset_input', default='./data', type=str,
                                     help='dataset_input (default: %(default)s)')
            args, _ = self.parser.parse_known_args()
            name_no_ext, _ = os.path.splitext(args.dataset_input)
            return os.path.join(self._prepare.dataset_path, name_no_ext)

        if data_type == DataType.MODEL:
            self.parser.add_argument('--model_input', default='./data', type=str,
                                     help='dataset_input (default: %(default)s)')
            args, _ = self.parser.parse_known_args()
            name_no_ext, _ = os.path.splitext(args.model_input)
            return os.path.join(self._prepare.pretrain_model_path, name_no_ext)
        if data_type == DataType.CODE:
            self.parser.add_argument('--code_input', default='./data', type=str,
                                     help='dataset_input (default: %(default)s)')
            args, _ = self.parser.parse_known_args()
            name_no_ext, _ = os.path.splitext(args.code_input)
            return os.path.join(self._prepare.code_path, name_no_ext)
        jcwLogger.error(f"Unknown data type for input: {data_type}")
        return ""

    def output_prepare(self, data_type: str, file_path: str):
        self.output = os.path.join(self._prepare.output_path, file_path)
        return self.output
