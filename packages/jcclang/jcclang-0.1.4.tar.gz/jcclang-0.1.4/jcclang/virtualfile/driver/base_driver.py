class Driver:
    def open(self, path: str, mode: str = "rb") -> str:
        """
        打开一个远程文件，返回 file_id 或 handler。
        - path: 存储路径（URL、bucket/key、本地路径）
        - mode: 默认 "rb" (read binary)
        """

    def stat(self, file_id: str) -> dict:
        """
        获取文件元信息，例如：
        {
            "size": 102400,
            "mtime": 1698888888,
            "etag": "xxxx"
        }
        """

    def read(self, file_id: str, offset: int, length: int) -> bytes:
        """
        从文件中读取指定范围的数据。
        - offset: 起始位置
        - length: 读取字节数
        """

    def close(self, file_id: str) -> None:
        """
        关闭文件连接，释放资源。
        """
