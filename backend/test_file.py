import unittest
from file import DataManager
import os

class TestDataManager(unittest.TestCase):
    """
    DataManager核心功能测试类，覆盖菜单加载、随机推荐、表头、异常、空菜单等。
    每个测试用例均输出日志，便于排查和回归。
    """
    def setUp(self):
        print("[TestDataManager] setUp: 创建测试菜单文件\n")
        # 使用测试数据文件
        self.test_csv = os.path.join(os.path.dirname(__file__), 'test_menu.csv')
        with open(self.test_csv, 'w', encoding='utf-8-sig') as f:
            f.write('食堂,楼层,窗口,餐品,预算\n')
            f.write('一食堂,一楼,窗口A,米饭,10\n')
            f.write('二食堂,二楼,窗口B,面条,12\n')
        self.dm = DataManager(menu_path=self.test_csv)
    
    
    
    def test_menu_load(self):
        print("[TestDataManager] test_menu_load: 测试菜单加载")
        self.assertEqual(len(self.dm.menu_data), 2)
        self.assertEqual(self.dm.menu_data[0]['餐品'], '米饭')
    
    def test_random_dish(self):
        print("[TestDataManager] test_random_dish: 测试随机推荐")
        dish = self.dm.random_dish()
        self.assertIn(dish['餐品'], ['米饭', '面条'])
        dish = self.dm.random_dish()
    
    def test_get_menu_header(self):
        print("[TestDataManager] test_get_menu_header: 测试表头获取")
        header = self.dm.get_menu_header()
        self.assertIn('食堂', header)
        self.assertIn('餐品', header)
        self.assertIn('食堂', header)
    
    def test_empty_menu(self):
        print("[TestDataManager] test_empty_menu: 测试自动搜索菜单文件，文件不存在会自动找寻目录下的菜单文件")
        empty_csv = os.path.join(os.path.dirname(__file__), 'empty.csv')
        dm2 = DataManager(menu_path=empty_csv)
        self.assertIn("食堂",dm2.menu_data[0])
 
    def test_get_distance(self):
        print("[TestDataManager] test_get_distance: 测试楼间距离查询")
        # 正常查询
        dist = self.dm.get_distance('宁远楼', '一食堂')
        self.assertEqual(dist, 2, "宁远楼到一食堂距离应为2")
        dist = self.dm.get_distance('博学楼', '惠园餐厅')
        self.assertEqual(dist, 1, "博学楼到惠园餐厅距离应为1")
        # 异常查询（教学楼不存在）
        dist = self.dm.get_distance('不存在的楼', '一食堂')
        self.assertIsNone(dist, "不存在的教学楼应返回None")
        # 异常查询（食堂不存在）
        dist = self.dm.get_distance('宁远楼', '不存在的食堂')
        self.assertIsNone(dist, "不存在的食堂应返回None")

if __name__ == '__main__':
    unittest.main()
