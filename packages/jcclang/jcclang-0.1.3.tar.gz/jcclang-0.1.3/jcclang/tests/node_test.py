# import json
#
# from jcclang.nodes.data_return_node import DataReturnNode
# from jcclang.nodes.train_node import AITrainNode
#
#
# def test_node():
#     # 训练节点
#     train_node = AITrainNode(
#         localJobID="1",
#         name="trainingtask-kdsrdtueyyxi",
#         description="sas",
#         files={
#             "dataset": {"type": "Binding", "bindingID": 1020},
#             "model": {"type": "Binding", "bindingID": 1023},
#             "image": {"type": "Image", "imageID": 37},
#         },
#         jobResources={
#             "scheduleStrategy": "dataLocality",
#             "clusters": [{
#                 "clusterID": "1865927992266461184",
#                 "runtime": {"envs": {}, "params": {}},
#                 "code": {"type": "Binding", "bindingID": 1025},
#                 "resources": [
#                     {"type": "STORAGE", "name": "disk", "number": 1024},
#                     {"type": "CPU", "name": "CPU", "number": 8},
#                     {"type": "MEMORY", "name": "RAM", "number": 50},
#                     {"type": "MEMORY", "name": "VRAM", "number": 40},
#                     {"type": "GPU", "name": "A100", "number": 1},
#                 ]
#             }]
#         }
#     )
#
#     # 数据返回节点，依赖训练节点
#     return_node = DataReturnNode(
#         localJobID="4",
#         targetJob=[{
#             "targetJobID": "1",
#             "inputParams": {
#                 "PackageName": "Name",
#                 "ClusterID": "ClusterID",
#                 "Output": "Output"
#             }
#         }]
#     ).depends_on(train_node)
#
#     print(train_node.name)
#
#     # 导出 IR
#     print(json.dumps(train_node.to_dict(), indent=2))
#     print(json.dumps(return_node.to_dict(), indent=2))
