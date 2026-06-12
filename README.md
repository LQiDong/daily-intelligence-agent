# Daily Intelligence Agent

每日智能信息抓取 Agent，自动收集科技、金融、AI 领域的最新事件，去重、分类、评分、总结，并通过邮件发送日报。

## 功能特性

- **多源信息抓取**：支持 RSS、NewsAPI、GDELT、Alpha Vantage、arXiv 等多种信息源
- **智能去重**：基于 URL 精确匹配 + 标题 Jaccard 相似度去重
- **AI 分类与评分**：按科技 / 金融 / AI 三大模块分类，5 维度加权评分（影响力、相关性、可信度、时效性、新颖性）
- **LLM 摘要**：支持 OpenAI / Anthropic，每条新闻输出一句话结论 + 核心事实 + 为什么重要 + 可能影响
- **双格式日报**：Markdown + HTML（移动端自适应）
- **自动邮件推送**：SMTP 发送，支持失败重试，密码日志脱敏
- **GitHub Actions 自动化**：定时 + 手动触发

## 项目结构

```
.
├── .github/workflows/
│   └── daily_report.yml      # GitHub Actions 自动运行配置
├── src/
│   ├── main.py                # 应用入口
│   ├── config/                # 配置管理（Pydantic Settings）
│   ├── collect/               # 信息抓取模块（5 个采集器）
│   ├── process/               # 数据处理（清洗、去重、分类、评分）
│   ├── generate/              # LLM 摘要 + 日报渲染（MD / HTML）
│   ├── send/                  # 邮件发送（SMTP + 重试）
│   └── utils/                 # 工具函数
├── reports/                   # 生成的日报文件
├── tests/                     # 测试用例（103+ 个测试）
├── .env                       # 环境变量（不提交到 Git）
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖
├── CLAUDE.md                  # 开发规范
└── README.md                  # 项目说明
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

### 3. 本地运行

```bash
python src/main.py
```

### 4. 运行测试

```bash
pytest tests/ -v
```

## 配置说明

### 核心环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_PROVIDER` | LLM 提供商 (`openai` / `anthropic`) | openai |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `ANTHROPIC_API_KEY` | Anthropic API Key | - |
| `SMTP_HOST` | SMTP 服务器地址 | smtp.gmail.com |
| `SMTP_PORT` | SMTP 端口 | 587 |
| `SMTP_USER` | 发件邮箱 | - |
| `SMTP_PASSWORD` | 邮箱授权码 / App Password | - |
| `EMAIL_TO` | 收件人地址 | - |
| `NEWSAPI_API_KEY` | NewsAPI.org API Key | - |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API Key | - |

> `SMTP_PASSWORD` 不要填写邮箱登录密码。Gmail 用户在 [Google App Passwords](https://myaccount.google.com/apppasswords) 生成应用专用密码；其他邮箱填写 SMTP 授权码。

### 采集器开关

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `COLLECTOR_RSS_ENABLED` | RSS 采集器 | true |
| `COLLECTOR_NEWSAPI_ENABLED` | NewsAPI 采集器 | true |
| `COLLECTOR_GDELT_ENABLED` | GDELT 采集器 | true |
| `COLLECTOR_ALPHA_VANTAGE_ENABLED` | Alpha Vantage 采集器 | true |
| `COLLECTOR_ARXIV_ENABLED` | arXiv 论文采集器 | true |

## 部署：GitHub Actions

`.github/workflows/daily_report.yml` 已配置好，推送代码到 GitHub 仓库即可启用。

### 1. 推送代码到 GitHub

```bash
git remote add origin https://github.com/your-username/daily-intelligence-agent.git
git branch -M main
git push -u origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库 **Settings → Secrets and variables → Actions → New repository secret** 中添加以下 Secrets。

**必填（不配置则日报无法完整运行）:**

| Secret | 对应 .env 变量 | 说明 | 获取方式 |
|--------|---------------|------|---------|
| `LLM_API_KEY` | `OPENAI_API_KEY` | LLM API 密钥 | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `EMAIL_USER` | `SMTP_USER` | 发件邮箱地址 | 你的邮箱地址 |
| `EMAIL_PASSWORD` | `SMTP_PASSWORD` | 邮箱授权码 / App Password | Gmail: [App Passwords](https://myaccount.google.com/apppasswords) |
| `EMAIL_TO` | `EMAIL_TO` | 日报收件人邮箱 | 目标邮箱地址 |

**选填（采集器 API Key，不配置对应采集器自动跳过）:**

| Secret | 对应 .env 变量 | 说明 |
|--------|---------------|------|
| `NEWS_API_KEY` | `NEWSAPI_API_KEY` | NewsAPI.org API 密钥 |
| `ALPHA_VANTAGE_API_KEY` | `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API 密钥 |

> **最小配置建议**：只需设置 `LLM_API_KEY` + `EMAIL_USER` + `EMAIL_PASSWORD` + `EMAIL_TO` 四项，即可收到带 LLM 摘要的完整日报。RSS、arXiv、GDELT 采集器无需 API Key，开箱即用。

### 3. 触发运行

**自动运行（定时）：**
- 每天 **北京时间 08:00** 自动执行
- GitHub Actions 的 `schedule` 基于 UTC 时间，当前配置 `0 0 * * *` 对应 UTC 00:00 = 北京时间 08:00

**手动运行：**
1. 打开 GitHub 仓库页面
2. 点击顶部 **Actions** 选项卡
3. 在左侧 Workflows 列表中点击 **Daily Intelligence Report**
4. 点击右侧 **Run workflow** 按钮
5. （可选）在弹出面板中选择日志级别：`DEBUG` / `INFO` / `WARNING`
6. 点击 **Run** 即可立即触发一次运行

### 4. 查看运行日志

1. 在 **Actions** 页面点击正在运行或已完成的 Workflow
2. 点击 **daily-report** job 查看完整日志
3. 日志中会打印：
   - 哪些采集器启动了 / 跳过了
   - 每种采集器采集到多少文章
   - 分类结果分布（ai / tech / finance / general）
   - 评分范围
   - 报告生成路径
   - 邮件发送结果

### 5. 下载 Reports Artifact

即使邮件发送失败，`reports/` 目录中的日报文件也会自动上传为 Artifact：

1. 在 Workflow 运行详情页底部找到 **Artifacts** 面板
2. 点击 **daily-reports** 下载 `.zip` 文件
3. 解压后包含两份文件：
   - `report_YYYY_MM_DD.md` — Markdown 格式日报
   - `report_YYYY_MM_DD.html` — HTML 格式日报（移动端自适应）

> `if: always()` 保证了无论前序步骤是否失败（包括邮件发送失败），Artifact 上传步骤都会执行。

## 故障排查

### 1. Workflow 运行失败（红色 ❌）

**检查步骤：**
1. 点击失败的工作流 → 展开报错的 Step
2. 查看具体错误信息
3. 常见原因：
   - `LLM_API_KEY` 未设置 → 添加该 Secret 后重试
   - 网络超时 → 检查 `HTTP_TIMEOUT` 是否过短
   - Python 版本不兼容 → 确保 workflow 中 `PYTHON_VERSION` 与 `requirements.txt` 兼容

### 2. 收不到邮件

**检查步骤：**
1. 进入 Workflow 日志，搜索 `EmailSender` 或 `email` 关键词
2. 看到 `SMTP credentials not configured` → 未设置 `EMAIL_USER` / `EMAIL_PASSWORD`
3. 看到 `EMAIL_TO not configured` → 未设置 `EMAIL_TO`
4. 看到 `Email send failed after 3 attempts` → SMTP 账号或密码错误
5. Gmail 用户特别注意：
   - 需要开启两步验证
   - 在 [App Passwords](https://myaccount.google.com/apppasswords) 生成专用密码
   - **不要使用邮箱登录密码**
6. 即使邮件发失败，**Artifact 中仍有日报文件**可下载

### 3. 采集器无数据

**检查步骤：**
1. 查看日志中对应采集器名称
2. `API Key not set, skipping` → 设置对应 Secrets 后重试
3. `429 Too Many Requests` → 免费 API 触发限流，稍后再试
4. RSS / arXiv / GDELT 无需 Key，日志无报错则检查网络连通性

### 4. 报告模块为空

**原因：** 采集到的文章经分类器后全部归入 `general` 类别，未能进入 AI / Tech / Finance 三大模块。

**解决方法：**
- 检查 RSS 源是否覆盖目标领域
- 增加更多 RSS 订阅源
- 手动触发时选择 `DEBUG` 日志级别，查看分类器详细命中情况

### 5. 本地手动调试

```bash
# 完整运行（跳过邮件发送，需要本地 .env 配置）
python src/main.py

# 带 DEBUG 日志运行
LOG_LEVEL=DEBUG python src/main.py

# 只启用部分采集器
COLLECTOR_NEWSAPI_ENABLED=false COLLECTOR_ALPHA_VANTAGE_ENABLED=false python src/main.py

# 运行全部测试
pytest tests/ -v --tb=short
```

### 6. 时区说明

GitHub Actions 的 `schedule` 使用 **UTC 时间**。当前配置：
- 每天 **北京时间 08:00** → `cron: "0 0 * * *"`（UTC 00:00）
- 如需更改时区：计算目标时间减去 UTC 偏移量，例如东京时间 08:00（UTC+9）→ `0 23 * * *`

## 开发规范

详见 [CLAUDE.md](CLAUDE.md)
