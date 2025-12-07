def log(message: str, level: str = "INFO"):
    """
    简单日志输出函数。
    Args:
        message (str): 日志内容。
        level (str): 日志级别，如 INFO、ERROR、DEBUG。
    """
    print(f"[{level}] {message}")
