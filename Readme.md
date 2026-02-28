# 猫大食堂智能推荐系统

## 项目简介

本项目是一个基于 Python Flask + HTML 的食堂智能推荐系统 Demo，前后端分离，集成 Deepseek API 实现 AI 对话。用户可通过网页与 AI 进行食堂菜品推荐对话，AI会根据用户输入的地点、口味、预算等信息智能推荐合适的餐品。

## 目录结构

```
Cateen/
├── backend/         # 后端服务（Flask）
│   ├── app.py       # 主服务代码，API接口
│   ├── requirements.txt # 依赖说明
│   └── todo.txt     # 研发计划/备忘
├── frontend/        # 前端页面
│   └── index.html   # 对话界面
├── Readme.md        # 项目说明
```

## 快速开始

### 1. 安装依赖

进入 `backend` 目录，安装依赖：

```bash
pip install flask flask-cors requests openai
```

### 2. 配置 Deepseek API

在 `app.py` 中填写你的 Deepseek API Key：

```python
DEEPSEEK_API_KEY = '你的API密钥'
```

### 3. 启动后端服务

```bash
python backend/app.py
```

### 4. 访问前端页面

浏览器访问 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 即可体验对话。

## 主要功能

- AI主动发起对话，模拟食堂推荐场景
- 用户输入地点、口味、预算等，AI智能推荐菜品
- 对话历史自动维护，支持上下文理解
- 前后端分离，静态页面自动由 Flask 服务

## 研发计划（见 `backend/todo.txt`）

- 支持数据导入（CSV/RAG）
- 支持流式对话
- 更多食堂数据和推荐逻辑

## 代码说明

- `backend/app.py`：详细注释，包含系统提示、用户提示、对话历史管理、API接口实现
- `frontend/index.html`：基础 HTML+JS，展示对话框，用户输入后与后端交互

## 其他说明

如需扩展推荐逻辑、接入更多数据或优化前端界面，请参考 `todo.txt` 并补充相关代码。
