# Daily Intelligence Agent — 开发规范

## 1. 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进，不使用 Tab
- 行长度限制 100 字符
- 使用双引号作为字符串引号（与 JSON 保持一致）

## 2. 项目架构原则

### 分层设计
- **collect**: 只负责从外部源获取原始数据，不做业务处理
- **process**: 负责数据清洗、去重、分类、评分等核心逻辑
- **generate**: 负责日报模板渲染和内容生成
- **send**: 负责邮件发送和推送
- **config**: 集中管理所有配置，统一从环境变量读取
- **utils**: 通用工具函数，禁止包含业务逻辑

### 依赖方向
上层可以调用下层，下层不能反向依赖上层：
`main → send/generate → process → collect → config/utils`

## 3. 配置管理

- 所有配置必须通过 `src/config/settings.py` 读取
- 禁止在代码中硬编码 API Key、密码等敏感信息
- 本地开发使用 `.env` 文件，生产环境使用环境变量
- 配置项使用 Pydantic Settings 进行类型校验

## 4. 日志规范

- 使用 `loguru` 作为日志库
- 日志格式：`{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}`
- 日志文件按天轮转，保留 7 天
- 禁止在代码中使用 `print()` 输出

## 5. 错误处理

- 外部 API 调用必须加 try-except 和重试机制
- 错误信息必须包含上下文（如请求的 URL、参数）
- 非致命错误记录日志后继续执行，不中断主流程
- 致命错误向上抛出，由 main.py 统一处理

## 6. 数据模型

- 使用 Pydantic 定义所有数据模型
- 模型文件放在各模块目录下，命名 `models.py`
- 字段命名使用 snake_case
- 时间字段统一使用 UTC，展示时转换为目标时区

## 7. 测试规范

- 使用 pytest 编写测试
- 测试文件命名：`test_*.py`
- 外部依赖使用 mock，禁止在测试中调用真实 API
- 核心逻辑覆盖率不低于 80%

## 8. Git 规范

- 分支：main（主分支）、feat/*（功能分支）、fix/*（修复分支）
- Commit message 使用中文，格式：`<类型>: <描述>`
- 类型：feat（新功能）、fix（修复）、docs（文档）、refactor（重构）、test（测试）
- 示例：`feat: 添加 RSS 源抓取模块`

## 9. 安全规范

- 禁止将 `.env` 文件提交到 Git
- 敏感信息（API Key、密码）必须通过环境变量注入
- HTTP 请求必须设置合理的超时时间（默认 30 秒）
- 用户输入和外部数据必须做校验和过滤
