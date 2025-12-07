import inspect
import os


def log(message: str, level: str = "INFO"):
    """
    日志输出，自动打印调用的文件名和方法名。
    Args:
        message (str): 日志内容。
        level (str): 日志级别，如 INFO、ERROR、DEBUG。
    """
    frame = inspect.currentframe().f_back
    filename = inspect.getfile(frame)
    funcname = frame.f_code.co_name
    lineno = frame.f_lineno
    print(f"[{level}] [{os.path.basename(filename)}::{funcname}:{lineno}] {message}")
