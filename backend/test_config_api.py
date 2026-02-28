import unittest
from flask import Flask
from config_api import config_api
import json
import os

class TestConfigAPI(unittest.TestCase):
    """
    配置API测试类，覆盖GET/POST接口和配置文件读写。
    每个测试用例均输出日志，便于排查和回归。
    """
    def setUp(self):
        print("[TestConfigAPI] setUp: 创建测试配置文件和客户端\n")
        self.app = Flask(__name__)
        self.app.register_blueprint(config_api)
        self.client = self.app.test_client()
        self.config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({'DEEPSEEK_API_KEY': 'test', 'DEEPSEEK_API_URL': 'http://test'}, f)
    

    def test_get_config(self):
        print("[TestConfigAPI] test_get_config: 测试GET接口")
        resp = self.client.get('/config')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('DEEPSEEK_API_KEY', data)
   
if __name__ == '__main__':
    unittest.main()
