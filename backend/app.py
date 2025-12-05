from openai import OpenAI
from flask import Flask, request, jsonify 
from flask_cors import CORS
import file

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
    menu_str = data_manager.get_menu_as_string()
    return f'''你是一个食堂推荐系统，请根据以下最新的菜单数据进行推荐：
{menu_str}

回复规则：
1. 必须基于上述数据推荐。
2. 如果用户没有提供足够信息（如辣度、价格），请追问。
3. 语气要亲切活泼。
'''


# 初始化消息历史，包含基于 CSV 的系统提示
msg_history = [{"role": "system", "content": get_system_prompt()}]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 获取用户消息
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({"reply": "请输入消息哦～"}), 400
        
        # 添加用户消息到历史
        msg_history.append({"role": "user", "content": user_message})
        
        # 调用 Deepseek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=msg_history,
            stream=False
        )
        
        # 获取AI回复
        ai_reply = response.choices[0].message.content
        
        # 将AI回复添加到历史
        msg_history.append({"role": "assistant", "content": ai_reply})
        
        print(f"AI回复: {ai_reply}")
        
        return jsonify({"reply": ai_reply})
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({"reply": "喵~ 抱歉,我现在有点忙不过来了,请稍后再试试吧~ 🙇‍♀️"}), 500

@app.route('/init', methods=['GET'])
def init():
    return jsonify({"reply": INIT_PROMPT})

@app.route('/reset', methods=['POST'])
def reset():
    global msg_history
    msg_history = [{"role": "system", "content": get_system_prompt()}]
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)