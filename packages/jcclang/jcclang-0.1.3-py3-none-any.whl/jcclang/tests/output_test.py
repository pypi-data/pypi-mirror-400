from jcclang.api.data_prepare import output_prepare
from jcclang.api.decorators import lifecycle
from jcclang.core.const import PLATFORM_MODELARTS, DataType


@lifecycle(platform=PLATFORM_MODELARTS)
def my_output():
    output_param = output_prepare(DataType.DATASET, "output111")
    return output_param


def test_output():
    my_output()
