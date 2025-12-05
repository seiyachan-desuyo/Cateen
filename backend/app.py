from openai import OpenAI
from flask import Flask, request, jsonify 
from flask_cors import CORS

# 创建Flask应用实例
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # 启用CORS

# Deepseek API配置
DEEPSEEK_API_URL = 'https://api.deepseek.com'
DEEPSEEK_API_KEY = 'sk-a29e901493ee46e290f20696adbfa4a3'  # 请替换为你的API Key

# AI初始提示
INIT_PROMPT = "嘿，京爷儿您来了，真地道,今儿吃点儿啥？ 想在食堂吃点啥呀？可以说说你现在在哪，或者赶不赶时间呢～"

SYSTEM_PROMPT = '''
你是一个食堂推荐系统，数据为：
{
input_data: 地点      , 菜品       , 价格, 标签(横线-分隔)
猫大一餐厅, 清真牛肉面 , 20 , 辣-清真-面食
猫大一餐厅, 红烧鸡腿   , 18 , 家常-鸡肉
猫咖      , 拿铁咖啡   , 25 , 饮品-咖啡
猫咖      , 蓝莓蛋糕   , 22 , 甜品-蛋糕
老虎餐厅 , 白斩鸡     , 30 , 粤菜
老虎餐厅 , 虎皮青椒   , 16 , 素菜-辣
} 
一个场景如下： 
贸小饭(AI)："同学好～今天想在食堂吃点啥呀？可以说说你现在在哪，或者赶不赶时间呢～"
用户："我现在在宁远楼，等下 1 点半有课，有点赶。"(用户主动说了 2 个关键信息：位置(宁远楼)、场景状态(赶课→想快点吃)
贸小饭(AI)："好嘞，宁远楼离清真食堂和一食堂都近，赶课的话咱们优先选快取的～想吃汤粉类的，还是偏米饭这类主食呀？"
用户："偏米饭的吧。"(用户说了形态偏好(偏米饭类，考虑现有套饭、黄焖鸡等))
贸小饭(AI)："好嘞，那今天想吃点清淡的，还是带点味道的呀？"
用户："想吃点辣的，但别太油，最近不想吃太腻的。"( 用户说了口味(辣)+ 隐性需求(不油→排除油炸)
贸小饭(AI)："懂了！辣的但不油，也就是排除油炸的。那有没有啥绝对不吃的呀(比如猪肉、鱼肉之类的)？还有今天吃饭想大概花多少钱呀？"
用户："没啥忌口，预算的话 12 到 15 块吧。"
贸小饭(AI)："好嘞！根据您的需求，推荐一食堂二楼--黄焖鸡窗口--「黄焖鸡米饭(13元)」：步行 6 分钟，黄焖鸡出餐较快；汤是辣口但不油，价格13元，符合预算～"
'''

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

# 初始化消息历史，包含系统提示
msg_history = [{"role": "system", "content": SYSTEM_PROMPT}]

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
    msg_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)