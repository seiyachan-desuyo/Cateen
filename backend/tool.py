import inspect
import os

def log(message: str, level: str = "INFO"):
    """
    日志输出，仅在DEBUG及以上等级时打印文件名、方法名和行号。
    Args:
        message (str): 日志内容。
        level (str): 日志级别，如 INFO、ERROR、DEBUG。
    """
    levels_with_detail = ["DEBUG", "ERROR"]
    if level.upper() in levels_with_detail:
        frame = inspect.currentframe().f_back
        filename = inspect.getfile(frame)
        funcname = frame.f_code.co_name
        lineno = frame.f_lineno
        print(f"[{level}] [{os.path.basename(filename)}::{funcname}:{lineno}] {message}")
    else:
        print(f"[{level}] {message}")
 