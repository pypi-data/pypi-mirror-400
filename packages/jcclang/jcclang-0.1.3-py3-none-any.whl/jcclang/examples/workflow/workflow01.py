from jcclang.core.const import Platform
from jcclang.nodes.bind_node import DatasetBindNode
from jcclang.nodes import DataReturnNode
from jcclang.nodes import AITrainNode

if __name__ == '__main__':
    train_job = AITrainNode(name="train-082801", description="")
    train_job.set_param("dataset_id", 2213)
    train_job.set_param("model_id", 2481)
    train_job.set_param("image_id", 43)
    train_job.set_param("schedule_strategy", "special")
    train_job.set_param("platform", Platform.MODELARTS)

    data_return = DataReturnNode(name="data-return01", description="")
    data_return.set_param("output", train_job.output("output"))
    data_return.set_param("platform", train_job.output("platform"))

    dataset_bind = DatasetBindNode(name="dataset-bind01", description="")
    dataset_bind.set_param("package_id", data_return.output("package_id"))
    dataset_bind.set_param("category", "image")
    dataset_bind.set_param("platforms", [Platform.OPENI, Platform.MODELARTS])
