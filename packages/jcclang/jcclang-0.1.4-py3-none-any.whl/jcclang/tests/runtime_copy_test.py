import os

def runtime_data_copy(remote_path: str, local_path: str):
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


if __name__ == '__main__':
    path = runtime_data_copy("/nudt-cloudream2/jcs2/users/180/dataset/fl_client_00/", "")
    print(path)
    print("finished")

