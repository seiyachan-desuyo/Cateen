import json
import os
from flask import Blueprint, request, jsonify

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
config_api = Blueprint('config_api', __name__)

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
         

@config_api.route('/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    return jsonify(load_config())

@config_api.route('/config', methods=['POST'])
def update_config():
    """更新配置"""
    cfg = request.json
    save_config(cfg)
    return jsonify({'status': 'success'})
