import importlib
import pkgutil
import sys
import types

# 要自动扫描的顶层子包列表（可根据需要增减）
子包列表 = [
    "html", "json", "mysql", "mysqlx", "公共API", "列表", "多线程", "多进程",
    "字典", "常量", "打印", "数学", "文件", "文本处理", "文本文件", "时间",
    "目录", "类型转换", "系统", "编码", "网页协议", "谷歌填表", "进程",
    "邮件IMAP", "邮件POP3", "配置文件"
]

def _挂载模块函数(包名):
    try:
        包 = importlib.import_module(f".{包名}", __name__)
    except ModuleNotFoundError:
        print(f"警告：未找到子包 {包名}")
        return

    # 遍历子模块
    for _, 模块名, ispkg in pkgutil.iter_modules(包.__path__, 包.__name__ + "."):
        if ispkg:
            # 子包递归
            _挂载模块函数(模块名.split('.')[-1])
        else:
            模块 = importlib.import_module(模块名)
            for 名 in dir(模块):
                if 名.startswith("_"):
                    continue  # 忽略私有函数
                if 名 not in globals():
                    globals()[名] = getattr(模块, 名)
                else:
                    # 冲突处理：加模块前缀
                    globals()[f"{模块名.split('.')[-1]}_{名}"] = getattr(模块, 名)

# 扫描并挂载所有顶层子包
for 子包 in 子包列表:
    _挂载模块函数(子包)