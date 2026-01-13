from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
import time


def 定时放行(目标时间: str) -> bool:
    """
    在每天指定时间进行一次阻塞等待，时间到达后立即放行。

    功能说明：
        - 目标时间使用 24 小时格式（例如 "09:30"、"23:05"）。
        - 若当前时间已经超过当天目标时间，则自动等待到“下一天同一时间”。
        - 函数在等待期间不会占用高 CPU（内部使用 sleep）。
        - 到达目标时间后返回 True，表示可以继续执行后续代码。
        - 任何异常都会被安全捕获并返回 False。

    Args:
        目标时间 (str):
            每天的目标触发时间，格式为 "HH:MM"。

    Returns:
        bool:
            - True：到达指定时间并成功放行。
            - False：参数无效或内部异常。

    Notes:
        - 本函数为“阻塞式等待”，适合单次定时放行的场景。
        - 若需要在后台循环每日触发，可在外层自行加入 while True 结构。
    """
    try:
        now = datetime.now()

        # 构造今天的目标时间
        today_str = now.strftime("%Y-%m-%d")
        target_dt = datetime.strptime(f"{today_str} {目标时间}", "%Y-%m-%d %H:%M")

        # 若今天已经错过 → 推迟到明天
        if now >= target_dt:
            target_dt += timedelta(days=1)

        # 计算需要等待的秒数
        wait_seconds = (target_dt - now).total_seconds()

        if wait_seconds > 0:
            time.sleep(wait_seconds)

        return True

    except Exception:
        return False