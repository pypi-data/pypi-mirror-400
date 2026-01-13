from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Union, Optional


_路径类型 = Union[str, Sequence[Any]]


def 取值_路径(
    数据: Any,
    键路径: _路径类型,
    默认值: Any = None,
    分隔符: str = ".",
    键转字符串: bool = True,
) -> Any:
    """
    根据“键路径”从嵌套结构中安全取值（dict/list 混合），失败返回默认值。

    功能说明：
        - 支持从多层嵌套结构中取值，避免层层判空与 KeyError/IndexError。
        - 路径支持两种形式：
            1) 字符串路径：如 "a.b.0.c"（使用分隔符拆分）
            2) 序列路径：如 ["a", "b", 0, "c"]（推荐：更精确）
        - 遍历过程中自动兼容：
            - 当前对象为 dict：按键取值（可选：键统一转字符串）
            - 当前对象为 list/tuple：按索引取值（索引可传 int，或可转 int 的字符串）
        - 任意一步取值失败、类型不匹配、路径不合法等，均返回默认值。
        - 不对返回对象做拷贝或修改，保持原始语义。

    行为说明：
        - 路径完整命中 → 返回最底层的值
        - 中途断路/类型不匹配/越界/键不存在 → 返回默认值

    Args:
        数据 (Any): 任意输入对象，通常为 dict/list 的嵌套结构。
        键路径 (str | Sequence[Any]): 路径字符串或路径序列。
        默认值 (Any): 失败时返回值，默认 None。
        分隔符 (str): 当键路径为字符串时的分隔符，默认 "."。
        键转字符串 (bool): 当走 dict 取值时，是否将键统一转换为 str。默认 True。

    Returns:
        Any:
            - 成功：返回路径命中的值
            - 失败：返回默认值
    """
    try:
        # 1) 归一化路径
        if isinstance(键路径, str):
            if 键路径 == "":
                return 默认值
            路径列表: List[Any] = 键路径.split(分隔符)
        elif isinstance(键路径, (list, tuple)):
            if len(键路径) == 0:
                return 默认值
            路径列表 = list(键路径)
        else:
            return 默认值

        当前 = 数据

        # 2) 逐段向下取值
        for 段 in 路径列表:
            if isinstance(当前, dict):
                键 = str(段) if 键转字符串 else 段
                if 键 in 当前:
                    当前 = 当前[键]
                else:
                    return 默认值

            elif isinstance(当前, (list, tuple)):
                # 允许 "0" / 0 两种写法
                try:
                    索引 = 段 if isinstance(段, int) else int(str(段))
                except Exception:
                    return 默认值

                if 0 <= 索引 < len(当前):
                    当前 = 当前[索引]
                else:
                    return 默认值
            else:
                return 默认值

        return 当前

    except Exception:
        return 默认值