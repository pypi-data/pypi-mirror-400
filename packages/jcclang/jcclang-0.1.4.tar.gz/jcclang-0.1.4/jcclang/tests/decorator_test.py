from jcclang.api.decorators import register_task


@register_task(alias="add", tags=["math", "basic"])
def add_task(inputs):
    return {"result": inputs["a"] + inputs["b"]}


def test_decorator():
    result = add_task({"a": 1, "b": 2})
    print(result)
