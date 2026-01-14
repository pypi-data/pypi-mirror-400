import logging
import os
import subprocess
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.Logger.Error = logging.Logger.error


def install_packages():
    packages = [
        "jcclang",
    ]
    for pkg in packages:
        logger.info(f"正在安装 {pkg} ...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pkg,
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])


try:
    from jcclang.api import input_prepare, output_prepare
    from jcclang.core.const import DataType
except ImportError:
    install_packages()
    from jcclang.api import input_prepare, output_prepare
    from jcclang.core.const import DataType

input_file_path = input_prepare(DataType.DATASET, '')
output_file_path = output_prepare(DataType.DATASET, 'train_output.txt')


def run():
    paths = os.listdir(input_file_path)
    print("输入文件路径:", input_file_path)
    print(paths)

    with open(output_file_path, "w", encoding="utf-8") as f:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(current_time + "\n")
        f.write("dataset path: ")
        f.write(str(paths))


if __name__ == '__main__':
    run()
