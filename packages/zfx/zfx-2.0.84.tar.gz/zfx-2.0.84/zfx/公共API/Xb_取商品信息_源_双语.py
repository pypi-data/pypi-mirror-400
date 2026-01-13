import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urlsplit, urlunsplit
from concurrent.futures import ThreadPoolExecutor


def Xb_取商品信息_源_双语(url: str) -> List[Optional[Dict[str, Any]]]:
    """
    从 Microsoft Xbox 商品详情页提取“预加载状态数据”（window.__PRELOADED_STATE__），
    同时获取“原始地区版本”和“繁体中文（zh-TW）版本”两份数据，并以列表形式返回。

    功能说明:
        - Xbox 商品详情页在页面脚本中内嵌了一个全局变量：
              window.__PRELOADED_STATE__ = {...}
          其中包含商品的基础元数据（标题、语言、地区、价格结构、图片等）。
        - 本函数会并行请求两个页面：
              1）调用方传入的原始 URL（例如 es-AR、en-US、zh-HK 等地区）
              2）基于同一商品路径自动构造的 zh-TW 版本 URL
        - 对每个页面，都会提取 window.__PRELOADED_STATE__ 并解析为 Python 字典。

    返回结构:
        - 返回一个长度为 2 的列表：
              [原始地区数据, 繁体中文(zh-TW)地区数据]
        - 每一项要么是 dict，要么是 None，对应以下 4 种组合之一：
              [原数据, 中文数据]
              [None,   中文数据]
              [原数据, None]
              [None,   None]

    错误处理:
        - 单个 URL 在任一步骤（网络/结构变化/JSON 解析）发生异常时，
          该 URL 对应结果为 None，不抛出异常到外部调用者。
        - 若整体出现未捕获异常，本函数也会返回 [None, None]。

    Args:
        url (str):
            Xbox 商品详情页完整 URL（任意地区，如 es-AR、en-US、zh-HK 等）。

    Returns:
        list[dict | None]:
            [原始地区数据, 繁体中文数据]
    """

    def _构造_zh_TW_url(原始url: str) -> str:
        """
        将任意地区的 Xbox 商品 URL 转换为 zh-TW 地区 URL。
        例如:
            https://www.xbox.com/es-ar/games/store/xxx/id/0001
        →  https://www.xbox.com/zh-TW/games/store/xxx/id/0001
        """
        try:
            parts = urlsplit(原始url)
            path = parts.path.lstrip("/")
            if not path:
                return 原始url

            segments = path.split("/")
            # 第一段通常是地区代码（如 es-AR、en-US、zh-HK 等）
            # 将其强制替换为 zh-TW
            segments[0] = "zh-TW"
            new_path = "/" + "/".join(segments)
            return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))
        except Exception:
            # 若解析失败，则退回原始 URL（后续请求失败会自然返回 None）
            return 原始url

    def _抓取单个页面(单个url: str) -> Optional[Dict[str, Any]]:
        """
        内部工具函数：
            - 对单个 URL 执行 3 次重试
            - 提取 window.__PRELOADED_STATE__ 并解析为 dict
            - 任意异常统一返回 None
        """
        try:
            resp = None

            # 固定重试 3 次
            for _ in range(3):
                try:
                    resp = requests.get(单个url, timeout=15)
                    if resp.status_code == 200:
                        break
                except Exception:
                    resp = None

            if resp is None or resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            脚本文本: Optional[str] = None
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

    try:
        zh_tw_url = _构造_zh_TW_url(url)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_original = executor.submit(_抓取单个页面, url)
            future_zh_tw = executor.submit(_抓取单个页面, zh_tw_url)

            try:
                原数据 = future_original.result()
            except Exception:
                原数据 = None

            try:
                中文数据 = future_zh_tw.result()
            except Exception:
                中文数据 = None

        return [原数据, 中文数据]

    except Exception:
        # 理论上很少会走到这里，作为兜底
        return [None, None]