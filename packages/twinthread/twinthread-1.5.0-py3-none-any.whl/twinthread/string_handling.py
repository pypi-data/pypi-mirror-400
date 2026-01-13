import base64


def test_task_encoding():
    id_str = "BatchB1-Predicted Humidity-2_462_4621"
    context = task_string_to_context(id_str)
    assert context["taskId"] == 462
    assert context["taskId"] == 4621


def task_string_to_context(task_string):
    [friendly, asset_model_id, operation_id, task_id] = task_string.split("_")

    return {
        "assetModelId": int(asset_model_id),
        "operationId": int(operation_id),
        "taskId": int(task_id),
        "friendly": friendly,
    }


def pretty_result(result):
    s = ""

    s += "Output\n----------\n"
    s += result["output"]
    s += "\nErrors\n----------\n"
    s += result["errors"] if result["errors"] else "None"
    s += "\n\n"

    return s
