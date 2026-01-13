import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any


def Xb_取商品信息_源(url: str) -> Optional[Dict[str, Any]]:
    """
    从 Microsoft Xbox 商品详情页提取“预加载状态数据”（window.__PRELOADED_STATE__），
    并解析为 Python 字典结构。

    功能说明:
        Xbox 商品详情页在页面脚本中内嵌了一个全局变量：
            window.__PRELOADED_STATE__ = {...}

        该变量包含商品的基础元数据（标题、地区信息、价格结构、图片等）。
        本函数通过请求页面 HTML，定位并提取这一段 JSON 文本，
        然后将其解析为 Python 字典，供后续程序使用。

    错误处理:
        - 任何阶段发生异常（网络/结构变化/JSON 解析失败）
        - 统一返回 None，不抛出异常到外部调用者

    Args:
        url (str):
            Xbox 商品详情页完整 URL。

    Returns:
        dict | None:
            - 成功：返回解析后的预加载状态数据（字典）
            - 失败：返回 None
    """
    try:
        resp = None

        # 固定重试 3 次
        for _ in range(3):
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    break
            except Exception:
                # 单次请求异常 → 继续重试
                resp = None

        # 三次都失败 或 最后一次不是 200
        if resp is None or resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        脚本文本 = None
        for s in soup.find_all("script"):
            t = s.string or ""
            if "__PRELOADED_STATE__" in t:
                脚本文本 = t
                break

        if not 脚本文本:
            return None

        目标 = "window.__PRELOADED_STATE__"
        pos = 脚本文本.find(目标)
        if pos == -1:
            return None

        start = 脚本文本.find("{", pos)
        if start == -1:
            return None

        level = 0
        end = start
        in_string = False
        escape = False

        for i in range(start, len(脚本文本)):
            ch = 脚本文本[i]

            if escape:
                escape = False
                continue

            if ch == '\\':
                escape = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if not in_string:
                if ch == "{":
                    level += 1
                elif ch == "}":
                    level -= 1

                if level == 0:
                    end = i + 1
                    break

        if end is None:
            return None

        json_like = 脚本文本[start:end]
        return json.loads(json_like)

    except Exception:
        return None