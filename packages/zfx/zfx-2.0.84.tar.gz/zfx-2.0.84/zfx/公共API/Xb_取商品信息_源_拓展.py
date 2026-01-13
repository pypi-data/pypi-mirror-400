import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor


def Xb_取商品信息_源_拓展(url: str) -> Optional[List[Optional[Dict[str, Any]]]]:
    """
    获取 Xbox 商品详情页的页面预加载数据与 Microsoft Store 扩展数据，
    并把两类信息统一整理后一起返回。

    功能说明:
        1) 访问商品详情页，解析脚本中的 window.__PRELOADED_STATE__，
           得到页面内部使用的预加载数据。
        2) 根据商品链接自动解析国家、语言与产品ID，
           调用 Microsoft Store 后端接口，获取更完整的产品信息结构。
        3) 网络请求具备多次尝试机制，提高成功率。
        4) 结果以列表形式返回：
               [页面预加载数据, 扩展接口数据]

    解析规则说明:
        - 链接路径通常包含“语言区域代码”（如 en-US、zh-CN 等）
        - 路径末尾包含产品唯一 ID
        - 函数会自动识别这些信息并完成请求

    错误处理:
        - 某一部分失败时，以 None 表示该部分失败。
        - 两部分都成功时，返回两个字典。
        - 极端异常情况下，整体返回 None。

    Args:
        url (str): Xbox 商品详情页完整 URL。

    Returns:
        list[dict | None] | None:
            - 成功: [源数据, 拓展数据]
            - 失败: None
    """

    def _解析_URL_地区与产品ID(url_: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        内部工具: 从 Xbox URL 中解析 (国家, 语言, 产品ID)。
        """
        try:
            parsed = urlsplit(url_)
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]

            语言_ = None
            国家_ = None
            产品ID_ = None

            # 第一段通常是 locale，例如 en-US / zh-CN / ja-JP
            if path_parts:
                first = path_parts[0]
                if "-" in first:
                    语言_ = first
                    国家_ = first.split("-")[-1].upper()

            # 兜底默认
            if not 语言_:
                语言_ = "en-US"
            if not 国家_:
                国家_ = "US"

            # 从后往前找一个非纯数字片段作为产品ID
            for seg in reversed(path_parts):
                seg = seg.strip()
                if not seg:
                    continue
                if seg.isdigit():
                    # 跳过类似 "0001"
                    continue
                产品ID_ = seg
                break

            return 国家_, 语言_, 产品ID_
        except Exception:
            return None, None, None

    def _取页面预加载数据(url_: str) -> Optional[Dict[str, Any]]:
        """
        内部工具: 请求 HTML 并解析 window.__PRELOADED_STATE__。
        含 3 次重试。
        """
        try:
            resp = None
            # 固定重试 3 次
            for _ in range(3):
                try:
                    resp = requests.get(url_, timeout=15)
                    if resp.status_code == 200:
                        break
                except Exception:
                    resp = None

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
            end = None
            in_string = False
            escape = False

            for i in range(start, len(脚本文本)):
                ch = 脚本文本[i]

                if escape:
                    escape = False
                    continue

                if ch == "\\":
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

    def _取商品信息_Ms_单ID(国家_: str, 语言_: str, 产品ID_: str) -> Optional[Dict[str, Any]]:
        """
        内部工具: 调用 Microsoft Store StoreEdgeFD 接口。
        只针对单个产品ID，但内部仍使用微软要求的格式。
        含 3 次重试。
        """
        try:
            if not 国家_ or not 语言_ or not 产品ID_:
                return None

            url_api = (
                "https://storeedgefd.dsx.mp.microsoft.com/v8.0/sdk/products"
                f"?market={国家_}&locale={语言_}&deviceFamily=Windows.Desktop"
            )

            payload = {"productIds": [产品ID_.strip()]}

            响应 = None
            for _ in range(3):
                try:
                    响应 = requests.post(url_api, data=payload, timeout=10)
                    if 响应.status_code == 200:
                        return 响应.json()
                except Exception:
                    响应 = None

            # 三次都失败
            return None

        except Exception:
            return None

    try:
        国家, 语言, 产品ID = _解析_URL_地区与产品ID(url)

        # 并行执行两个任务
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_源 = executor.submit(_取页面预加载数据, url)

            if 国家 and 语言 and 产品ID:
                future_拓展 = executor.submit(_取商品信息_Ms_单ID, 国家, 语言, 产品ID)
            else:
                future_拓展 = None

            源数据 = future_源.result()
            拓展数据 = future_拓展.result() if future_拓展 is not None else None

        return [源数据, 拓展数据]

    except Exception:
        # 理论上不会经常走到这里，属于兜底
        return None