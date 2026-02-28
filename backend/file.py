import os
import csv
import datetime
import random

from tool import log

class DataManager:


    @staticmethod
    def get_distance( building, canteen, distance_path=None):
        """
        查询指定教学楼到指定食堂的距离（1~5）。
        Args:
            building (str): 教学楼名
            canteen (str): 食堂名
            distance_path (str, optional): 距离表CSV路径
        Returns:
            int: 距离（1~5），未找到则返回 None
        """
        if not distance_path:
            distance_path = os.path.join(os.path.dirname(__file__), 'distance_table.csv')
        if not os.path.exists(distance_path):
            log(f"[DataManager] 未找到距离表文件: {distance_path}", level="ERROR")
            return None
        with open(distance_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['教学楼/食堂'] == building:
                    try:
                        return int(row.get(canteen, None))
                    except (ValueError, TypeError):
                        return None
        return None
    
    @staticmethod
    def find_menu_file(csv_path=None):
        """查找菜单CSV文件,优先当前工作目录、项目根目录、常用文件名"""
        base_dir = os.path.abspath(os.path.dirname(__file__))
        root_dir = os.path.abspath(os.path.join(base_dir, '..'))
        backend_dir = os.path.join(root_dir, 'backend')

        candidate_files = [
            csv_path,
            os.path.join(os.getcwd(), '食堂数据S1.csv'),
            os.path.join(os.getcwd(), '食堂数据.csv'),
            os.path.join(base_dir, '食堂数据S1.csv'),
            os.path.join(base_dir, '食堂数据.csv'),
            os.path.join(root_dir, '食堂数据S1.csv'),
            os.path.join(root_dir, '食堂数据.csv'),
            os.path.join(backend_dir, '食堂数据S1.csv'),
            os.path.join(backend_dir, '食堂数据.csv'),
        ]
        
        log("[DataManager] 菜单数据文件查找顺序:", level="DEBUG")
        for f in candidate_files:
            log(f"  尝试: {f} -> {'存在' if f and os.path.exists(f) else '不存在'}", level="DEBUG")
            if f and os.path.exists(f):
                log(f"[DataManager]选用菜单数据文件: {os.path.abspath(f)}", level="DEBUG")
                return os.path.abspath(f)
        raise FileNotFoundError("未找到菜单数据文件（如食堂数据S1.csv 或 食堂数据.csv），请将数据文件放在项目根目录或backend同级目录下！")

    def __init__(self, menu_path=None, log_path=None):
        """初始化 DataManager，加载菜单数据和日志路径。
        Args:
            csv_path (str, optional): 菜单CSV文件路径。
            log_path (str, optional): 会话日志CSV路径。
        """

        # 菜单数据列表
        self.menu_data = []

        # 智能查找菜单CSV文件路径
        self.menu_path = self.find_menu_file(menu_path)

        # 会话日志文件，保存在 backend 目录下
        if log_path:
            self.log_path = log_path
        else:
            self.log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conversation_log.csv'))

        

        # 读取菜单路径下的菜单数据
        try:
            self._load_menu()
            log(f"[DataManager][INFO] 菜单数据加载成功，共 {len(self.menu_data)} 条记录。", level="INFO")
        except Exception as e:
            log(f"[DataManager][ERROR] 加载菜单数据失败: {e}", level="ERROR")
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
        if not os.path.exists(self.menu_path):
            return
        with self._open_csv(self.menu_path, 'r') as f:
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

    def random_dish(self):
        """随机推荐一个菜品（返回字典或空）。"""
        if not self.menu_data:
            return None
        return random.choice(self.menu_data)

    def get_menu_header(self, csv_path=None):
        """返回菜单表头（字段名数组）"""
        if(self.menu_data is None):  
            self.menu_path = self.find_menu_file(csv_path)
        with open(self.menu_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            return [name.strip() for name in first_line.strip().split(',')]


    @staticmethod   
    def get_building_and_canteen_list(distance_path=None):
        """
        从距离表CSV文件中获取教学楼列表和食堂列表。
        Returns:
            (building_list, canteen_list)
        """
        if not distance_path:
            distance_path = os.path.join(os.path.dirname(__file__), 'distance_table.csv')
        building_list = []
        canteen_list = []
        if not os.path.exists(distance_path):
            return building_list, canteen_list
        with open(distance_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            canteen_list = header[1:]
            for row in reader:
                building_list.append(row[0])
        return building_list, canteen_list
    
    
    @staticmethod
    def extract_distance_info(user_message, distance_path=None):
        """
        判断用户消息中是否包含教学楼，并返回该楼到所有食堂的距离。
        Returns:
            (found_building, canteen_distances, distance_info)
        """
        building_list, canteen_list = DataManager.get_building_and_canteen_list(distance_path)
        found_building = None
        for b in building_list:
            if b in user_message:
                found_building = b
                break
        canteen_distances = {}
        distance_info = None
        if found_building:
            info_lines = []
            for c in canteen_list:
                distance = DataManager.get_distance(found_building, c, distance_path)
                canteen_distances[c] = distance
                info_lines.append(f"{found_building} 到 {c} 距离为 {distance}")
            distance_info = "【距离提示】\n" + "\n".join(info_lines)
        return found_building, canteen_distances, distance_info


#=================还没用的============

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


