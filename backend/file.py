import os
import csv
import datetime


class DataManager:
    def __init__(self, csv_path=None, log_path=None):
        # 默认 CSV 在项目根目录下的 '食堂数据.csv'
        if csv_path:
            self.csv_path = csv_path
        else:
            self.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '食堂数据 short.csv'))

        # 会话日志文件，保存在 backend 目录下
        if log_path:
            self.log_path = log_path
        else:
            self.log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conversation_log.csv'))

        self.menu_data = []
        self._load_menu()

    def _open_csv(self, path, mode='r'):
        # 尝试使用 utf-8-sig 解码，失败则退回到 gbk（Windows 常见）
        try:
            return open(path, mode, encoding='utf-8-sig', newline='')
        except UnicodeDecodeError:
            return open(path, mode, encoding='gbk', newline='')

    def _load_menu(self):
        self.menu_data = []
        if not os.path.exists(self.csv_path):
            return
        with self._open_csv(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.menu_data.append(row)

    def get_menu_as_string(self):
        if not self.menu_data:
            return '（当前菜单为空）'

        lines = []
        for item in self.menu_data:
            # 尝试使用常见字段名，若不存在则使用任意字段
            place = item.get('地点') or item.get('地点/窗口') or item.get('location') or item.get('place') or ''
            dish = item.get('菜品') or item.get('dish') or ''
            price = item.get('价格') or item.get('price') or ''
            tags = item.get('标签') or item.get('tags') or ''
            parts = []
            if place:
                parts.append(str(place))
            if dish:
                parts.append(str(dish))
            if price:
                parts.append(f"{price}元")
            if tags:
                parts.append(f"标签: {tags}")

            lines.append(' | '.join(parts))

        return '\n'.join(lines)

    def log_conversation(self, speaker, text):
        # 追加写入会话日志（CSV）: timestamp, speaker, text
        header = ['timestamp', 'speaker', 'text']
        exists = os.path.exists(self.log_path)
        with open(self.log_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(header)
            ts = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
            writer.writerow([ts, speaker, text])

    def add_dish(self, location, dish, price, tags=None):
        # 向 CSV 追加一行，并刷新内存中的菜单
        # 保证目录存在
        csv_exists = os.path.exists(self.csv_path)
        # 默认列名为中文，若已有文件则使用已有字段顺序
        if csv_exists:
            # 读取现有字段头
            with self._open_csv(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or ['地点', '菜品', '价格', '标签']
        else:
            fieldnames = ['地点', '菜品', '价格', '标签']

        row = {}
        # 尝试匹配常见字段名
        if '地点' in fieldnames:
            row['地点'] = location
        if '菜品' in fieldnames:
            row['菜品'] = dish
        if '价格' in fieldnames:
            row['价格'] = price
        if '标签' in fieldnames:
            row['标签'] = tags or ''

        # 如果 fieldnames 是英文，则尝试映射
        if any(fn.lower() in ('location', 'place') for fn in fieldnames):
            # fallback mapping
            row = {'地点': location, '菜品': dish, '价格': price, '标签': tags or ''}

        # 写入 CSV（追加），若文件不存在则写 header
        write_header = not os.path.exists(self.csv_path)
        with open(self.csv_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(fieldnames)
            # 构造输出行，按照 fieldnames 顺序
            out = []
            for fn in fieldnames:
                # 映射已有中文 keys
                if fn in row:
                    out.append(row.get(fn, ''))
                else:
                    # 若 fieldname 是英文，尝试基本映射
                    low = fn.lower()
                    if low in ('location', 'place'):
                        out.append(location)
                    elif low in ('dish', 'name'):
                        out.append(dish)
                    elif low in ('price',):
                        out.append(price)
                    elif low in ('tags', 'label'):
                        out.append(tags or '')
                    else:
                        out.append('')
            writer.writerow(out)

        # 重新加载菜单
        self._load_menu()
