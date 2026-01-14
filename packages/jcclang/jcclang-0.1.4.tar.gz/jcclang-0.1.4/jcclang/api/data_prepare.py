from jcclang.adapter import get_adapter
from jcclang.core.context import get_platform
from jcclang.core.logger import jcwLogger


def input_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        jcwLogger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.input_prepare(data_type, file_path)
    except Exception as e:
        jcwLogger.error("Error in input_prepare: {}".format(e))
        raise

    return path


def output_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        jcwLogger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.output_prepare(data_type, file_path)
    except Exception as e:
        jcwLogger.error("Error in output_prepare: {}".format(e))
        raise

    return path


def runtime_data_copy(remote_path: str, local_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        jcwLogger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.runtime_data_copy(remote_path, local_path)
    except Exception as e:
        jcwLogger.error("Error in runtime_data_copy: {}".format(e))
        raise

    return path
