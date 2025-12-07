import os
import csv
import datetime
import tool

class DataManager:
    @staticmethod
    def find_csv_file(csv_path=None):
        """查找菜单CSV文件,优先当前工作目录、项目根目录、常用文件名"""
        candidate_files = [
            csv_path,
            os.path.join(os.getcwd(), '食堂数据S1.csv'),
            os.path.join(os.getcwd(), '食堂数据.csv'),
            os.path.join(os.path.dirname(__file__), '..', '食堂数据S1.csv'),
            os.path.join(os.path.dirname(__file__), '..', '食堂数据.csv'),
        ]
        tool.log("[DataManager] 菜单数据文件查找顺序:", level="DEBUG")
        for f in candidate_files:
            tool.log(f"  尝试: {f} -> {'存在' if f and os.path.exists(f) else '不存在'}", level="DEBUG")
            if f and os.path.exists(f):
                tool.log(f"[DataManager]选用菜单数据文件: {os.path.abspath(f)}", level="DEBUG")
                return os.path.abspath(f)
        raise FileNotFoundError("未找到菜单数据文件（如食堂数据S1.csv 或 食堂数据.csv），请将数据文件放在项目根目录或backend同级目录下！")

    def __init__(self, csv_path=None, log_path=None):
        """初始化 DataManager，加载菜单数据和日志路径。
        Args:
            csv_path (str, optional): 菜单CSV文件路径。
            log_path (str, optional): 会话日志CSV路径。
        """

        # 智能查找菜单CSV文件路径
        self.csv_path = self.find_csv_file(csv_path)

        # 会话日志文件，保存在 backend 目录下
        if log_path:
            self.log_path = log_path
        else:
            self.log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conversation_log.csv'))

        self.menu_data = []

        # 读取菜单路径下的菜单数据
        try:
            self._load_menu()
            tool.log(f"[DataManager][INFO] 菜单数据加载成功，共 {len(self.menu_data)} 条记录。", level="INFO")
        except Exception as e:
            tool.log(f"[DataManager][ERROR] 加载菜单数据失败: {e}", level="ERROR")
            self.menu_data = []

    def _open_csv(self, path, mode='r'):
        """以合适的编码方式打开CSV文件，兼容utf-8-sig和gbk。
        Args:
            path (str): 文件路径。
            mode (str): 打开模式。
        Returns:
            file object: 打开的文件对象。
        """
        try:
            return open(path, mode, encoding='utf-8-sig', newline='')
        except UnicodeDecodeError:
            return open(path, mode, encoding='gbk', newline='')

    def _load_menu(self):
        """加载菜单数据到内存。以CSV第一行作为表头和字段名。"""
        self.menu_data = []
        if not os.path.exists(self.csv_path):
            return
        with self._open_csv(self.csv_path, 'r') as f:
            # 读取第一行作为表头
            first_line = f.readline()
            fieldnames = [name.strip() for name in first_line.strip().split(',')]
            reader = csv.DictReader(f, fieldnames=fieldnames)
            for row in reader:
                self.menu_data.append(row)

    def get_menu_as_string(self) -> str:
        """以字符串形式返回当前菜单内容（先输出表头，再输出内容）。"""
        if not self.menu_data:
            return '（当前菜单为空）'

        # 获取表头
        header = self.get_menu_header()
        lines = [', '.join(header)]
        for idx, item in enumerate(self.menu_data):
            row = [str(item.get(h, '')) for h in header]
            lines.append(', '.join(row))
        return '\n'.join(lines)

    @classmethod
    def get_menu_header(cls, csv_path=None):
        """返回菜单表头（字段名数组）"""
        path = cls.find_csv_file(csv_path)
        with open(path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            return [name.strip() for name in first_line.strip().split(',')]




    def log_conversation(self, speaker, text):
        """记录一条会话到日志文件。
        Args:
            speaker (str): 说话者（如user/ai）。
            text (str): 对话内容。
        """
        header = ['timestamp', 'speaker', 'text']
        exists = os.path.exists(self.log_path)
        with open(self.log_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(header)
            ts = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
            writer.writerow([ts, speaker, text])


