from openai import OpenAI
from flask import Flask, request, jsonify 
from flask_cors import CORS
import config_api
import json
import os
import random

from tool import log
from file import DataManager



# ===========初始化==================

# 创建Flask应用实例
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # 启用CORS
app.register_blueprint(config_api.config_api)

# 读取配置文件
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

DEEPSEEK_API_URL = config.get('DEEPSEEK_API_URL')
DEEPSEEK_API_KEY = config.get('DEEPSEEK_API_KEY')
INIT_PROMPT = config.get('INIT_PROMPT')

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

# 实例化 DataManager，从 CSV 读取菜单并记录会话
data_manager = DataManager()

def get_system_prompt():
    log("调用 get_system_prompt，生成系统提示...")
    menu_str = data_manager.get_menu_as_string()
    log(f"当前菜单数据：\n{menu_str}")
    return f'''你是一个食堂推荐系统，请根据以下最新的菜单数据进行推荐：
{menu_str}

回复规则：
1. 必须基于上述数据推荐。
2. 如果用户没有提供足够信息（如辣度、价格），请追问。
3. 语气要亲切活泼。
'''


# 初始化消息历史，包含基于 CSV 的系统提示
global_msg_history = [{"role": "system", "content": get_system_prompt()}]


# ==================路由方法==================

@app.route('/')
def index():
    log("[访问首页 /]，返回 index.html")
    return app.send_static_file('index.html')

@app.route('/random_dish', methods=['GET'])
def random_dish():
    """随机推荐一个菜品，返回json。"""

    log("[进入 /random_dish 路由]，随机推荐一个菜品...")
    dish = data_manager.random_dish()
    log(f"随机推荐菜品: {dish}")
    if dish:
        return jsonify({'success': True, 'dish': dish})
    else:
        return jsonify({'success': False, 'msg': '菜单为空，无法推荐'}), 404

@app.route('/dish_samples', methods=['GET'])
def dish_samples():
    """返回菜单中随机抽取的3个菜品样本。"""

    log("获取菜单样本...")
    menu = data_manager.menu_data or []
    if not menu:
        return jsonify({'success': False, 'msg': '菜单为空', 'samples': []}), 404
    samples = random.sample(menu, min(3, len(menu)))

    log(f"随机抽取的菜品样本: {samples}")
     
    return jsonify({'success': True, 'samples': samples})

@app.route('/chat', methods=['POST'])
def chat():
    log("[进入 /chat 路由]，收到请求...")
    try:
        # 获取用户消息
        json_data = request.get_json(silent=True)
        user_message = json_data.get('message', '') if json_data else ''
        log(f"用户消息: {user_message}")
        
        if not user_message:
            log("用户消息为空，返回提示...")
            return jsonify({"reply": "请输入消息哦～"}), 400
        
        # 检查用户消息中是否包含教学楼名，并获取距离
        found_building, canteen_distances, distance_info = DataManager.extract_distance_info(user_message)
        if distance_info:
            log(distance_info)
        
        # 构造带距离信息的用户输入
        user_message_with_distance = user_message
        if found_building :
            distance_lines = [f"{found_building}到{canteen}距离为{dist} " for canteen, dist in canteen_distances.items()]
            user_message_with_distance += "\n" + "\n".join(distance_lines)
        
        # 添加用户消息到历史
        global_msg_history.append({"role": "user", "content": user_message_with_distance})
        log(f"当前消息历史: {global_msg_history}")
        
        # 调用 Deepseek API
        log("调用 Deepseek API...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=global_msg_history,
            stream=False
        )
        
        # 获取AI回复
        ai_reply = response.choices[0].message.content
        if distance_info:
            ai_reply = distance_info + "\n" + ai_reply
        log(f"AI回复: {ai_reply}")
        
        # 将AI回复添加到历史
        global_msg_history.append({"role": "assistant", "content": ai_reply})
        log(f"更新后消息历史: {global_msg_history}")
        
        return jsonify({"reply": ai_reply})
    
    except ValueError as ve:
        log(f"/chat 路由ValueError: {str(ve)}", level="ERROR")
        return jsonify({"reply": "喵~ 抱歉,输入有误，请检查后重试~ 🙇‍♀️"}), 400
    except Exception as e:
        log(f"/chat Exception异常: {str(e)}", level="ERROR")
        return jsonify({"reply": "喵~ 抱歉,我现在有点忙不过来了,请稍后再试试吧~ 🙇‍♀️"}), 500


# 初始化对话，AI先发起 
@app.route('/init', methods=['GET'])
def init():
    log("[进入 /init 路由]，返回初始AI提示...")
    return jsonify({"reply": INIT_PROMPT})


@app.route('/reset', methods=['POST'])
def reset():
    """重置对话历史和系统提示"""
    log("[进入 /reset 路由]，重置对话历史...")
    global global_msg_history
    global_msg_history = [{"role": "system", "content": get_system_prompt()}]
    log("对话历史已重置。")
    return jsonify({"status": "success"})


#  ========= MAIN =========

if __name__ == '__main__':
    log("启动 Flask 服务，监听 0.0.0.0:5000 ...")
    app.run(debug=True, host='0.0.0.0', port=5000)
