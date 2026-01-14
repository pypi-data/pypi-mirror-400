import argparse
import os
from pathlib import Path

from jcclang.adapter.base_adapter import BaseAdapter
from jcclang.core.const import DataType
from jcclang.core.logger import jcwLogger


class ModelArtsAdapter(BaseAdapter):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Model Training with input parameter')
        self.output = ""

    def before_task(self, inputs, context: dict):
        jcwLogger.info("modelarts before task")

    def after_task(self, outputs, context: dict):
        jcwLogger.info("modelarts after task, output", self.output)

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            if not any(a.dest == 'dataset_input' for a in self.parser._actions):
                self.parser.add_argument('--dataset_input', default='./data', type=str,
                                         help='dataset_input (default: %(default)s)')
        elif data_type == DataType.MODEL:
            if not any(a.dest == 'model_input' for a in self.parser._actions):
                self.parser.add_argument('--model_input', default='./models', type=str,
                                         help='model_input (default: %(default)s)')
        elif data_type == DataType.CODE:
            if not any(a.dest == 'code_input' for a in self.parser._actions):
                self.parser.add_argument('--code_input', default='./src', type=str,
                                         help='code_input (default: %(default)s)')
        else:
            jcwLogger.error(f"Unknown data type for input: {data_type}")
            return ""

        args, _ = self.parser.parse_known_args()

        base_path = ""
        if data_type == DataType.DATASET:
            base_path = args.dataset_input
        elif data_type == DataType.MODEL:
            base_path = args.model_input
        elif data_type == DataType.CODE:
            base_path = args.code_input

        path = Path(base_path) / file_path
        return path

    def output_prepare(self, data_type: str, file_path: str):
        if not any(a.dest == 'output' for a in self.parser._actions):
            self.parser.add_argument('--output', default='/output', type=str,
                                     help='output (default: %(default)s)')
        args, _ = self.parser.parse_known_args()
        path = Path(args.output) / file_path
        return path.as_posix()

    def runtime_data_copy(self, remote_path: str, local_path: str):
        import moxing as mox
        """
        将 OBS 上的一个“目录”同步到本地，并返回本地路径。

        Args:
            obs_key_path (str): OBS 对象路径，格式如 '/bucket/key/prefix/' 或 'bucket/key/prefix/'
                                支持以 '/' 开头或不以 '/' 开头。
            local_base_dir (str): 本地根目录，用于存放下载内容。默认为当前目录 './'

        Returns:
            str: 本地实际保存文件的目录路径（绝对路径）

        Example:
            local_path = sync_obs_dir_to_local('/nudt-cloudream2/jcs2/users/180/dataset/fl_client_00/')
            # 会在 ./jcs2/users/180/dataset/fl_client_00/ 下保存文件
        """
        # 1. 标准化输入路径：去除首尾空格，确保是字符串
        obs_key_path = remote_path.strip()

        # 2. 处理开头斜杠：统一移除开头的 '/'
        if obs_key_path.startswith('/'):
            obs_key_path = obs_key_path[1:]

        # 3. 拆分 bucket 和 object key
        parts = obs_key_path.split('/', 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid OBS path: must contain at least 'bucket/key', got: {obs_key_path}")

        bucket_name = parts[0]
        object_prefix = parts[1]

        # 4. 确保 object_prefix 以 '/' 结尾（便于 list_directory）
        if not object_prefix.endswith('/'):
            object_prefix += '/'

        # 5. 构造完整的 obs:// URL
        obs_url = f"obs://{bucket_name}/{object_prefix}"

        # 6. 本地路径：local_base_dir + object_prefix（不含 bucket）
        local_dir = os.path.abspath(os.path.join(local_path, object_prefix.lstrip('/')))

        # 7. 创建本地目录
        os.makedirs(local_dir, exist_ok=True)

        # 8. 列出 OBS 目录下的所有文件
        try:
            file_list = mox.file.list_directory(obs_url)
        except Exception as e:
            raise RuntimeError(f"Failed to list OBS directory: {obs_url}") from e

        if not file_list:
            print(f"Warning: No files found in {obs_url}. Local dir created but empty.")
            return local_dir

        # 9. 逐个下载文件
        for filename in file_list:
            src_file = f"{obs_url}{filename}"  # obs://bucket/prefix/filename
            dst_file = os.path.join(local_dir, filename)
            print(f"Downloading: {src_file} -> {dst_file}")
            mox.file.copy(src_file, dst_file)

        return local_dir
