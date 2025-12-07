from openai import OpenAI
from flask import Flask, request, jsonify 
from flask_cors import CORS
import file
import tool

# ===========初始化==================

# 创建Flask应用实例
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # 启用CORS

# Deepseek API配置
DEEPSEEK_API_URL = 'https://api.deepseek.com'
DEEPSEEK_API_KEY = 'sk-a29e901493ee46e290f20696adbfa4a3'  # 请替换为你的API Key
 
# AI初始提示
INIT_PROMPT = "嘿，京爷儿您来了，真地道,今儿吃点儿啥？ 想在食堂吃点啥呀？可以说说你现在在哪，或者赶不赶时间呢～"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

# 实例化 DataManager，从 CSV 读取菜单并记录会话
data_manager = file.DataManager()






def get_system_prompt():
    tool.log("调用 get_system_prompt，生成系统提示...")
    menu_str = data_manager.get_menu_as_string()
    tool.log(f"当前菜单数据：\n{menu_str}")
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
    tool.log("访问首页 /，返回 index.html")
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    tool.log("进入 /chat 路由，收到请求...")
    try:
        # 获取用户消息
        user_message = request.json.get('message', '')
        tool.log(f"用户消息: {user_message}")
        
        if not user_message:
            tool.log("用户消息为空，返回提示...")
            return jsonify({"reply": "请输入消息哦～"}), 400
        
        # 添加用户消息到历史
        global_msg_history.append({"role": "user", "content": user_message})
        tool.log(f"当前消息历史: {global_msg_history}")
        
        # 调用 Deepseek API
        tool.log("调用 Deepseek API...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=global_msg_history,
            stream=False
        )
        
        # 获取AI回复
        ai_reply = response.choices[0].message.content
        tool.log(f"AI回复: {ai_reply}")
        
        # 将AI回复添加到历史
        global_msg_history.append({"role": "assistant", "content": ai_reply})
        tool.log(f"更新后消息历史: {global_msg_history}")
        
        return jsonify({"reply": ai_reply})
    
    except Exception as e:
        tool.log(f"/chat 路由异常: {str(e)}", level="ERROR")
        return jsonify({"reply": "喵~ 抱歉,我现在有点忙不过来了,请稍后再试试吧~ 🙇‍♀️"}), 500


# 初始化对话，AI先发起 
@app.route('/init', methods=['GET'])
def init():
    tool.log("进入 /init 路由，返回初始AI提示...")
    return jsonify({"reply": INIT_PROMPT})


@app.route('/reset', methods=['POST'])
def reset():
    """重置对话历史和系统提示"""
    tool.log("进入 /reset 路由，重置对话历史...")
    global global_msg_history
    global_msg_history = [{"role": "system", "content": get_system_prompt()}]
    tool.log("对话历史已重置。")
    return jsonify({"status": "success"})


#  ========= MAIN =========

if __name__ == '__main__':
    tool.log("启动 Flask 服务，监听 0.0.0.0:5000 ...")
    app.run(debug=True, host='0.0.0.0', port=5000)
