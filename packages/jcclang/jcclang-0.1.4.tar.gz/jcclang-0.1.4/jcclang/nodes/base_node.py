from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict, Generic, TypeVar, List
from urllib.parse import urlparse, parse_qs

import requests


# 作用是 在类型注解中引入泛型（generic types），让函数、类能支持多种类型，而不仅仅是写死的某个类型。
TInputs = TypeVar("TInputs")
TOutputs = TypeVar("TOutputs")


class OutputRef:
    def __init__(self, node: "Node", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


# 通过 Generic[T] 告诉类型检查器：这个类依赖于一个类型参数 T，Generic[T] 的主要作用是 声明类的类型参数
# TypeVar 定义类型变量。 Generic 让类声明自己支持哪些类型变量。 两者配合，才能写出泛型类，就像 list[T]、dict[K, V] 一样。
class Node(Generic[TInputs, TOutputs]):
    id_counter = 0

    def __init__(self, name: str, node_type, description: str):
        Node.id_counter += 1
        self.id = str(Node.id_counter)
        self.node_type = node_type
        self.name = name
        self.description = description
        self.dependencies: list[str] = []
        self.params: Dict[str, Any] = {}
        self.ref_params: Dict[str, Any] = {}
        self.inputs: TInputs = None  # 子类会填
        self.outputs: TOutputs = None  # 子类会填
        # 自动注册到 workflow
        workflow.add_node(self)

    def set_param(self, key: str, value: Any):
        # 类型检查
        if not hasattr(self.inputs, key):
            raise AttributeError(f"Invalid param '{key}' for {self.__class__.__name__}")

        if isinstance(value, OutputRef):
            value.key = param_mapping(value.key)
            self.ref_params[param_mapping(key)] = value
            # 判断self.dependencies是否已经有id
            if value.node.id not in self.dependencies:
                self.dependencies.append(value.node.id)
            return self
        self.params[key] = value
        return self

    def output(self, key: str) -> OutputRef:
        if not hasattr(self.outputs, key):
            raise AttributeError(f"Invalid output '{key}' for {self.__class__.__name__}")
        return OutputRef(self, key)

    def to_dict(self) -> Dict[str, Any]:
        def serialize(value: Any):
            if isinstance(value, OutputRef):
                return value.resolve()
            return value

        self.name = self.name or f"{self.__class__.__name__}_{self.id}" + "_" + str(int(time.time()))

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.node_type,
            "depends_on": self.dependencies,
            "params": {k: serialize(v) for k, v in self.params.items()},
            "ref_params": {k: serialize(v) for k, v in self.ref_params.items()},
        }


class Workflow:
    def __init__(self, filename="workflow"):
        self.nodes: List["Node"] = []
        self.filename = filename
        self.package_id = 0
        self.user_id = 0
        self.bootstrap_id = 0

    def add_node(self, node: "Node"):
        jcwLogger.info(f"add node: {node.id}")
        # 判断是否存在
        if node.id in [n.id for n in self.nodes]:
            return

        self.nodes.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "packageID": self.package_id,
            "userID": self.user_id,
            "bootstrapObjID": self.bootstrap_id,
        }

    def add_external_node(self):
        jcwLogger.debug("add external node")
        # 设置开始与结束节点依赖关系
        lastNodeID = ""
        endIndex = -1
        startIndex = -1
        for i in range(len(self.nodes)):
            jcwLogger.debug(f"index: {i}, node id: {self.nodes[i].id}")
            if self.nodes[i].id == NodeID.FIRST_ID:
                self.nodes[i].dependencies.append(NodeID.START_ID)
                continue

            # 1、ID从1开始自增；2、开始和结束节点ID不是自增，所以需要-2
            if int(self.nodes[i].id) == len(self.nodes) - 2:
                lastNodeID = self.nodes[i].id
                continue

            if self.nodes[i].id == NodeID.START_ID:
                startIndex = i
                continue

            if self.nodes[i].id == NodeID.END_ID:
                endIndex = i

        # 将开始节点挪到第一个
        if startIndex != -1:
            self.nodes.insert(0, self.nodes.pop(startIndex))

        if endIndex != -1 and lastNodeID != "":
            jcwLogger.debug(f"add dependency: {self.nodes[endIndex].id} -> {lastNodeID}")
            self.nodes[endIndex].dependencies.append(lastNodeID)

    def save_on_exit(self):
        url = ""
        if len(sys.argv) > 1:
            url = sys.argv[1]

        if url == "":
            # url 为空，不做任何事
            jcwLogger.info(f"the code executed successfully")
            return

        jcwLogger.debug(f"receive url: {url}")

        self.add_external_node()

        if url == "file":
            name = self.filename + "_" + str(int(time.time())) + ".json"
            with open(name, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            jcwLogger.info(f"workflow saved to {self.filename}")
            return

        # 校验url
        if not (url.startswith("https://") or url.startswith("http://")):
            jcwLogger.error(f"Invalid url: {url}")
            return

        # http://localhost:7891/jcweaver/parse?packageID=16&userID=5&token=1234567890，提取出packageID和token
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        self.package_id = int(params['packageID'][0])  # 获取 packageID 的值: "1"
        self.user_id = int(params['userID'][0])  # 获取 packageID 的值: "1"
        self.bootstrap_id = int(params['bootstrapObjID'][0])
        token = params['token'][0]  # 获取 token 的值: "1234567890"

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": token,
            }
            jcwLogger.info(f"posting workflow: {self.to_dict()}")
            resp = requests.post(url, json=self.to_dict(), headers=headers, timeout=10)
            resp.raise_for_status()
            jcwLogger.info(f"workflow posted to {url}, status={resp.status_code}")
        except Exception as e:
            jcwLogger.error(f"failed to post workflow: {e}")


# 全局 workflow 实例
workflow = Workflow()
