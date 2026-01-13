from typing import Any, Dict, Type


_类型中文映射: Dict[Type[Any], str] = {
    list: "列表",
    dict: "字典",
    tuple: "元组",
    set: "集合",
    str: "字符串",
    int: "整数",
    float: "浮点数",
    bool: "布尔值",
    type(None): "空值",
}


def 打印变量类型(变量: Any) -> None:
    """
    打印给定变量的运行时类型信息（包含中文说明）。

    本函数用于调试与诊断场景，输出变量的 Python 类型名称，
    并在其后附加对应的中文类型说明，便于快速理解变量结构。

    设计约定：
        - 类型名称始终来自运行时 ``type``，保证准确性。
        - 中文说明仅作为辅助信息，不影响程序逻辑。
        - 未在映射表中的类型，将显示为“自定义类型”。

    Args:
        变量 (Any): 任意 Python 对象。

    Returns:
        None
    """
    try:
        变量类型 = type(变量)
        中文说明 = _类型中文映射.get(变量类型, "自定义类型")

        print(f"变量类型: {变量类型.__name__}（{中文说明}）")
    except Exception as 异常:
        print(f"变量类型获取失败: {异常}")