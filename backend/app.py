from openai import OpenAI

# 导入Flask相关库和第三方库
from flask import Flask, request, jsonify  # Flask用于Web服务，request处理请求，jsonify返回JSON响应
from flask_cors import CORS  # 允许跨域请求，便于前后端分离开发
import requests  # 用于向Deepseek API发送HTTP请求

# 创建Flask应用实例，指定静态文件目录为前端文件夹（../frontend），静态URL路径为根目录
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # 启用CORS，允许所有来源访问API

# Deepseek API相关配置
DEEPSEEK_API_URL = 'https://api.deepseek.com'  # Deepseek对话API的URL
DEEPSEEK_API_KEY = 'sk-a29e901493ee46e290f20696adbfa4a3'  # 请替换为你的Deepseek API Key

# AI对话的初始提示，AI会先发起对话
INIT_PROMPT = "嘿，京爷儿您来了，真地道,今儿吃点儿啥？ 想在食堂吃点啥呀？可以说说你现在在哪，或者赶不赶时间呢～"  # AI的开场白，用户可以根据需要修改

SYSTEM_PROMPT = '''
你是一个食堂推荐系统，数据为：
{
input_data: 地点      , 菜品       , 价格, 标签（横线-分隔）
猫大一餐厅, 清真牛肉面 , 20 , 辣-清真-面食
猫大一餐厅, 红烧鸡腿   , 18 , 家常-鸡肉
猫咖      , 拿铁咖啡   , 25 , 饮品-咖啡
猫咖      , 蓝莓蛋糕   , 22 , 甜品-蛋糕
老虎餐厅 , 白斩鸡     , 30 , 粤菜
老虎餐厅 , 虎皮青椒   , 16 , 素菜-辣
} 
一个场景如下： 
贸小饭（AI）：“同学好～今天想在食堂吃点啥呀？可以说说你现在在哪，或者赶不赶时间呢～”
用户：“我现在在宁远楼，等下 1 点半有课，有点赶。”（用户主动说了 2 个关键信息：位置（宁远楼）、场景状态（赶课→想快点吃）
贸小饭（AI）：“好嘞，宁远楼离清真食堂和一食堂都近，赶课的话咱们优先选快取的～想吃汤粉类的，还是偏米饭这类主食呀？”
用户：“偏米饭的吧。”（用户说了形态偏好（偏米饭类，考虑现有套饭、黄焖鸡等））
贸小饭（AI）：AI：“好嘞，那今天想吃点清淡的，还是带点味道的呀？”
用户：想吃点辣的，但别太油，最近不想吃太腻的。”（ 用户说了口味（辣）+ 隐性需求（不油→排除油炸）
贸小饭（AI）：““懂了！辣的但不油，也就是排除油炸的。那有没有啥绝对不吃的呀（比如猪肉、鱼肉之类的）？还有今天吃饭想大概花多少钱呀？”
用户：“没啥忌口，预算的话 12 到 15 块吧。”
贸小饭（AI）：“好嘞！根据您的需求，推荐一食堂二楼--黄焖鸡窗口--「黄焖鸡米饭（13元）」：步行 6 分钟，黄焖鸡出餐较快；汤是辣口但不油，价格13元，符合预算～”
'''

USER_PROMPT = '我赶时间，要吃15块的挂面, 带点辣 我在教学楼'

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

msg_hisory = []  # 用于存储用户消息历史，便于后续对话上下文处理

# 根路由，返回前端页面index.html
@app.route('/')
def index():
    # 直接返回静态文件夹中的index.html，实现前后端分离部署
    return app.send_static_file('index.html')

# 聊天接口，接收用户消息并转发给Deepseek API，返回AI回复
@app.route('/chat', methods=['POST'])
def chat():
    # 如果是空数组
    if not msg_hisory:
        msg_hisory.append({"role": "system", "content": SYSTEM_PROMPT }) 
    
    # 获取前端发送的JSON数据   用户输入的消息
    user_message = request.json.get('message', '')
      
     
    msg_hisory.append({"role": "user", "content": user_message })  # 将用户消息添加到历史记录中


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=msg_hisory,
        stream=False
    )

    print(response.choices[0].message.content)


    if response.choices[0].message.content:
        # 成功时，提取AI回复内容并返回给前端
        ai_reply = response.choices[0].message.content
        return jsonify({"reply": ai_reply})
    else:
        # 失败时，返回错误信息
        return jsonify({"reply": "AI服务暂时不可用。"}), 500

# 初始化接口，前端首次加载时获取AI的开场白
@app.route('/init', methods=['GET'])
def init():
    return jsonify({"reply": INIT_PROMPT})

# 启动Flask开发服务器
if __name__ == '__main__':
    app.run(debug=True)  # debug=True便于开发调试，生产环境请关闭
