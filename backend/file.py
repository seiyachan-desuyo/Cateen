# 文件读写 
# file.py
import csv
import os
import datetime

class DataManager:
    def __init__(self, menu_file='menu.csv', log_file='chat_history.log'):
        self.menu_file = menu_file
        self.log_file = log_file
        self.menu_data = []
        self.load_menu()

    def load_menu(self):
        """读取CSV文件并加载到内存中"""
        if not os.path.exists(self.menu_file):
            print(f"警告: {self.menu_file} 不存在")
            return
        
        self.menu_data = []
        with open(self.menu_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.menu_data.append(row)
        print(f"成功加载 {len(self.menu_data)} 道菜品。")

    def get_menu_as_string(self):
        """将菜单数据格式化为Prompt需要的字符串格式"""
        if not self.menu_data:
            return "暂无菜单数据"
        
        result = "地点      , 菜品       , 价格, 标签\n"
        for item in self.menu_data:
            result += f"{item['地点']}, {item['菜品']}, {item['价格']}, {item['标签']}\n"
        return result

    def log_conversation(self, role, content):
        """记录聊天日志到文件"""
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time_str}] {role}: {content}\n")
            f.write("-" * 30 + "\n")

    def add_dish(self, location, dish, price, tags):
        """(加分项) 提供一个Python函数来添加新菜品"""
        new_dish = {'地点': location, '菜品': dish, '价格': price, '标签': tags}
        self.menu_data.append(new_dish)
        
        # 追加写入文件
        file_exists = os.path.exists(self.menu_file)
        with open(self.menu_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['地点', '菜品', '价格', '标签']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_dish)
        return True