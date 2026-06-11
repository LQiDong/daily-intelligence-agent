# Daily Intelligence Agent

每日智能信息抓取 Agent，自动收集科技、金融、AI 领域的最新事件，去重、分类、评分、总结，并通过邮件发送日报。

## 功能特性

- **多源信息抓取**：支持 RSS、API 等多种信息源
- **智能去重**：基于内容相似度的去重机制
- **AI 分类与评分**：使用 LLM 对新闻进行分类和重要性评分
- **自动邮件推送**：定时生成并发送结构化日报
- **模块化架构**：易于扩展新的信息源和处理逻辑

## 项目结构

```
.
├── src/
│   ├── main.py              # 应用入口
│   ├── config/              # 配置管理
│   ├── collect/             # 信息抓取模块
│   ├── process/             # 数据处理（去重、分类、评分）
│   ├── generate/            # 日报生成
│   ├── send/                # 邮件发送
│   └── utils/               # 工具函数
├── data/                    # 本地数据存储
├── logs/                    # 日志文件
├── tests/                   # 测试用例
├── .env                     # 环境变量（不提交到 Git）
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key 和邮箱配置
```

### 3. 运行

```bash
python src/main.py
```

## 配置说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_MODEL` | 使用的模型 | gpt-4o |
| `SMTP_HOST` | SMTP 服务器地址 | smtp.gmail.com |
| `SMTP_USER` | 发件邮箱 | - |
| `SMTP_PASSWORD` | 邮箱授权码/密码 | - |
| `EMAIL_TO` | 收件人地址 | - |
| `SCHEDULED_TIME` | 每日发送时间 | 08:00 |

## 开发规范

详见 [CLAUDE.md](CLAUDE.md)
