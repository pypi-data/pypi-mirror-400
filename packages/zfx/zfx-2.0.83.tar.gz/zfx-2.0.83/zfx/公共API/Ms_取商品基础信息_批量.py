import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor


def 安全取值(数据, 路径, 默认=None):
    """
    从嵌套的 dict / list 结构中安全取值。
    取值失败时返回 默认。
    """
    当前 = 数据
    for 键 in 路径:
        if isinstance(当前, dict):
            当前 = 当前.get(键)
        elif isinstance(当前, list) and isinstance(键, int):
            当前 = 当前[键] if 0 <= 键 < len(当前) else None
        else:
            return 默认
        if 当前 is None:
            return 默认
    return 当前


def _合并_Ms_双语言数据(英文数据, 中文数据) -> List[Dict[str, Any]]:
    """
    根据 ProductId 把英文与中文结果合并为统一结构列表。

    返回示例：
    [
        {
            "产品ID": "...",
            "英文标题": "...",
            "中文标题": "...",
            "开发商名称": "...",
            "发行商名称": "...",
            "描述": "..."
        },
        ...
    ]
    """
    结果字典: Dict[str, Dict[str, Any]] = {}

    # ---------- 先处理英文 ----------
    if 英文数据:
        for 商品数据 in 英文数据:
            产品ID = 安全取值(商品数据, ["ProductId"])
            if not 产品ID:
                continue

            结果字典[产品ID] = {
                "产品ID": 产品ID,
                "英文标题": 安全取值(商品数据, ["LocalizedProperties", 0, "ProductTitle"]),
                "中文标题": None,
                "开发商名称": 安全取值(商品数据, ["LocalizedProperties", 0, "DeveloperName"]),
                "发行商名称": 安全取值(商品数据, ["LocalizedProperties", 0, "PublisherName"]),
                "打折期限": 安全取值(商品数据, ["DisplaySkuAvailabilities", 0, "Availabilities", 0, "Conditions", "EndDate"]),
                "描述": 安全取值(商品数据, ["LocalizedProperties", 0, "ProductDescription"]),
            }

    # ---------- 再补充中文 ----------
    if 中文数据:
        for 商品数据 in 中文数据:
            产品ID = 安全取值(商品数据, ["ProductId"])
            if not 产品ID:
                continue

            if 产品ID not in 结果字典:
                # 英文没返回，但中文有
                结果字典[产品ID] = {
                    "产品ID": 产品ID,
                    "英文标题": None,
                    "中文标题": 安全取值(商品数据, ["LocalizedProperties", 0, "ProductTitle"]),
                    "开发商名称": None,
                    "发行商名称": None,
                    "打折期限": None,
                    "描述": None,
                }
            else:
                # 在已有结构上补充中文标题
                结果字典[产品ID]["中文标题"] = 安全取值(
                    商品数据, ["LocalizedProperties", 0, "ProductTitle"]
                )

    return list(结果字典.values())


def Ms_取商品基础信息_批量(ID列表: List[str]) -> List[Dict[str, Any]]:
    """
    从 Microsoft Store 官方服务接口获取产品基础信息（StoreEdgeFD 后端接口），此功能基于微软官方API返回数据二次处理，随时面临失效，具体效果自行测试，不建议长期使用。

    功能说明:
    - 通过官方后端接口获取产品的标题、描述、开发商、发行商等基础信息。
    - 返回的数据可直接用于展示、存储或进一步处理。

    参数:
        ID列表 (List[str]):
            Microsoft Store 产品 ID 组成的列表。
            列表长度为 1–25，空值会被自动忽略。

    返回:
        list[dict]:
            成功时返回产品信息列表，每一项包含（若缺失则为 None）：
                - "产品ID"
                - "英文标题"
                - "中文标题"
                - "开发商名称"
                - "发行商名称"
                - "描述"
            发生错误或无有效数据时返回空列表 []。

    注意事项:
        - 该接口属于 Microsoft Store 客户端使用的服务端地址，
          并非公开稳定 API，随时可能发生调整或限制。
        - 返回结构在不同地区、系统版本或产品类型下可能存在差异。
        - 本函数仅用于学习与测试，不适合用于生产环境或商业用途。

    ⚠️ 免责声明:
        本函数调用的接口 (storeedgefd.dsx.mp.microsoft.com)
        为 Microsoft Store 客户端使用的后端通信端点，
        目前未在微软公开文档中列为正式 API。
        其返回结构、访问权限及可用性可能随系统或地区变化。
    """
    英文结果 = None
    中文结果 = None

    try:
        # ----------- 基础校验 -----------
        if not isinstance(ID列表, list) or not ID列表:
            return []
        if len(ID列表) > 25:
            return []

        合并ID = ",".join(str(i).strip() for i in ID列表 if i)
        if not 合并ID:
            return []

        def _请求_指定语言(locale: str):
            try:
                payload = {"productIds": [合并ID]}
                url = (
                    "https://storeedgefd.dsx.mp.microsoft.com/v8.0/sdk/products"
                    f"?market=US&locale={locale}&deviceFamily=Windows.Desktop"
                )

                # 最多重试 3 次
                for _ in range(3):
                    try:
                        r = requests.post(url, data=payload, timeout=10)
                        if r.status_code == 200:
                            数据 = r.json().get("Products")
                            return 数据 if isinstance(数据, list) else None
                    except Exception:
                        # 单次请求异常，忽略并继续重试
                        pass
                return None
            except Exception:
                return None

        # ----------- 并行请求英文 / 中文 -----------
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_en = executor.submit(_请求_指定语言, "en-US")
            future_zh = executor.submit(_请求_指定语言, "zh-CN")

            英文结果 = future_en.result()
            中文结果 = future_zh.result()

    except Exception:
        # 出现意外，统一返回空列表
        return []

    # ----------- 合并结果并返回 -----------
    合并后列表 = _合并_Ms_双语言数据(英文结果, 中文结果)
    return 合并后列表