# V2G聚合平台

这是一个V2G（Vehicle-to-Grid，车联网）聚合平台，用于管理电动汽车放电任务和监控。

## 项目结构

```
v2g/
├── backend/              # 后端服务
│   ├── app.py            # 主应用入口
│   ├── models/           # 数据模型
│   ├── utils/            # 工具函数
│   └── requirements.txt  # 依赖项
├── frontend/             # 前端页面
│   ├── index.html        # 主页面
│   ├── styles/           # CSS样式
│   └── utils/            # JavaScript工具
└── README.md             # 项目说明
```

## 功能特性

### 后端
- Flask Web框架
- 任务管理API
- 缓存管理（LRUCache、TwoLevelCache）
- 数据持久化

### 前端
- 放电任务创建和管理
- 实时监控
- 提醒功能
- 响应式设计

## 启动步骤

### 1. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端服务将在 `http://127.0.0.1:5000` 启动。

### 2. 启动前端服务

```bash
cd frontend
python -m http.server 8000
```

前端服务将在 `http://localhost:8000` 启动。

## 使用说明

1. 打开浏览器访问 `http://localhost:8000`
2. 在首页创建放电任务
3. 查看任务列表和状态
4. 接收任务提醒

## 技术栈

- **后端**: Python, Flask, SQLite
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **缓存**: LRU Cache, Redis (可选)
- **响应式设计**: CSS Grid, Flexbox

## 开发说明

### 环境配置

后端使用Flask开发模式，调试功能已启用。
前端使用原生JavaScript，无需构建工具。

### API接口

- `POST /task`: 创建放电任务
- `GET /tasks`: 获取任务列表
- `PUT /task/<id>`: 更新任务状态
- `DELETE /task/<id>`: 删除任务

## 许可证

MIT License
