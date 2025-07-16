# 微信群聊每日报告生成器

这是一个自动化的微信群聊记录分析工具，可以每天自动拉取指定群聊的聊天记录，使用AI进行智能总结，并生成结构化的日报发送给用户。

## 🌟 功能特点

- 🤖 **智能总结**: 支持OpenAI GPT、Google Gemini等AI服务对聊天记录进行智能分析和总结
- 📱 **多群监控**: 可同时监控多个微信群聊
- ⏰ **自动化运行**: 支持cron和systemd定时任务，每天自动生成报告
- 📧 **多种通知方式**: 支持邮件、控制台输出、思源笔记等多种报告发送方式
- 🔧 **灵活配置**: 支持本地简单总结和AI智能总结两种模式
- 📊 **结构化报告**: 生成包含群聊活跃度、核心话题、FAQ、待跟进事项等的结构化报告
- 📓 **思源笔记集成**: 自动保存报告到思源笔记，支持结构化存储和标签管理

## 📋 项目结构

```
wechat_daily_report/
├── main.py                 # 主程序入口
├── requirements.txt        # Python依赖
├── .env.example           # 配置文件模板
├── setup_scheduler.sh     # 定时任务设置脚本
├── src/                   # 源代码目录
│   ├── wechat_client.py   # 微信API客户端
│   ├── summarizer.py      # AI总结服务
│   ├── report_generator.py # 报告生成器
│   └── siyuan_client.py   # 思源笔记客户端
├── templates/             # 报告模板
├── reports/              # 生成的报告文件
└── logs/                 # 日志文件
```

## 🚀 快速开始

### 1. 环境要求

- **Python**: 3.8+
- 本地运行的微信聊天记录API服务 (http://127.0.0.1:5030)
- (可选) OpenAI API密钥或Google Gemini API密钥用于智能总结
- (可选) 思源笔记软件用于报告存储

### 2. 安装依赖

```bash
# 克隆或下载项目到本地
cd wechat_daily_report

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置设置

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
vi .env  # 或使用其他编辑器
```

配置文件说明：

```bash
# API设置
WECHAT_API_BASE_URL=http://127.0.0.1:5030
WECHAT_API_TIMEOUT=30

# 目标群聊（用逗号分隔群名或群ID）
TARGET_GROUPS=今天HR被鸽了吗🐶,工作群,朋友圈

# AI服务设置
AI_SERVICE=gemini  # 可选: openai, gemini, local
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# 邮件通知设置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=your_email@gmail.com

# 思源笔记集成
SIYUAN_ENABLED=true
SIYUAN_BASE_URL=http://127.0.0.1:6806
SIYUAN_NOTEBOOK_ID=20250207155248-so9nz4m
SIYUAN_AUTH_TOKEN=your_siyuan_api_token
SIYUAN_SAVE_INDIVIDUAL_GROUPS=false

# 报告设置
MAX_MESSAGES_PER_GROUP=200
```

### 4. 测试运行

```bash
# 测试API连接和配置
python main.py --test

# 手动生成报告
python main.py

# 生成指定日期的报告
python main.py --date 2023-12-01
```

### 5. 设置自动化定时任务

```bash
# 运行定时任务设置脚本
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

或手动设置cron任务：

```bash
# 编辑crontab
crontab -e

# 添加每天早上8点运行的任务
0 8 * * * cd /path/to/wechat_daily_report && python main.py
```

## 📖 详细使用说明

### AI服务配置

#### 1. OpenAI模式
```bash
AI_SERVICE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # 或 gpt-4
```

#### 2. Google Gemini模式 (推荐)
```bash
AI_SERVICE=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash  # 或 gemini-1.5-pro
```

**Gemini优势**：
- 💰 成本更低
- ⚡ 处理速度快
- 📄 支持更长的上下文

#### 3. 本地模式 (无需API密钥)
```bash
AI_SERVICE=local
```

### 群聊配置

在`TARGET_GROUPS`中配置要监控的群聊，支持：
- 群聊昵称：`今天HR被鸽了吗🐶`
- 群聊ID：`24254678513@chatroom`

### 思源笔记集成

**功能特点**：
- 🗂️ **优化目录结构**：日报扁平化存储 (`/微信群聊日报/2024-01-15-日报`)
- 📁 **群聊分类存储**：按群聊名称分文件夹 (`/微信群聊日报/群聊报告/工作群/2024-01-15.md`)
- 📊 **数据统计表格**：包含各群聊消息数量和处理状态
- 🏷️ **智能标签**：自动添加日期、类型等标签便于检索
- 🔗 **文档关联**：支持相关文档的链接引用
- 📝 **格式优化**：专为思源笔记优化的Markdown格式

**配置步骤**：

1. **获取笔记本ID**：
   - 打开思源笔记
   - 在设置 → 关于 → 笔记本列表中找到目标笔记本ID

2. **获取API Token**：
   - 思源笔记设置 → API → 生成Token
   - 将Token配置到`SIYUAN_AUTH_TOKEN`

3. **配置示例**：
```bash
SIYUAN_ENABLED=true
SIYUAN_BASE_URL=http://127.0.0.1:6806
SIYUAN_NOTEBOOK_ID=20250207155248-so9nz4m
SIYUAN_AUTH_TOKEN=p5jtu1bzgwwx7wdk
SIYUAN_SAVE_INDIVIDUAL_GROUPS=false  # 是否为每个群聊创建单独文档
```

### 邮件通知配置

支持Gmail等SMTP服务：

```bash
# Gmail配置示例
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # 使用应用专用密码
```

**Gmail设置步骤**：
1. 启用两步验证
2. 生成应用专用密码
3. 使用应用密码而非账户密码

### 报告模板自定义

可以在`templates/daily_report.md`中自定义报告模板：

```markdown
# {{ report_date }} 微信群聊日报

**生成时间**: {{ generation_time }}

{% for summary in summaries %}
{{ summary.summary }}
{% endfor %}
```

## 📊 生成的报告格式

### 结构化总结包含：

- **📊 群聊概况**：参与人数、消息统计、活跃时间
- **🔥 核心话题**：按重要性排序的主要讨论内容
- **💡 有价值信息**：重要通知、资源分享、经验总结
- **❓ FAQ常见问题**：自动整理的问答内容
- **🎯 待跟进事项**：需要后续关注的任务清单
- **📝 备注**：其他值得关注的信息

### 示例报告片段：

```markdown
## 📊 群聊概况
- **群聊名称**: 产品讨论群
- **活跃成员**: 12人
- **消息总数**: 156条
- **时间跨度**: 2024-01-15 09:00 ~ 18:30

## 🔥 核心话题

1. **新版本功能规划**: 
   - 核心内容: 讨论V2.0版本的核心功能点
   - 主要观点: 优先级应该放在用户体验优化上
   - 参与讨论: 张三、李四、王五

## ❓ FAQ 常见问题

**Q1**: 新功能什么时候上线？
**A1**: 预计下个月底完成开发，下下个月初发布

## 🎯 待跟进事项
- [ ] 确认UI设计方案 (张三负责)
- [ ] 制定测试计划 (李四负责)
```

## 🔧 API接口说明

本项目基于 [chatlog](https://github.com/sjzar/chatlog) 项目的API接口：

- `/api/v1/chatlog` - 获取聊天记录
- `/api/v1/chatroom` - 获取群聊列表
- `/api/v1/session` - 获取会话列表

## ❗ 故障排除

### 1. API连接失败
```bash
# 检查chatlog服务是否运行
curl http://127.0.0.1:5030/api/v1/session?format=json&limit=1&offset=0

# 确保端口5030未被占用
netstat -tlnp | grep 5030
```

### 2. 找不到群聊
```bash
# 查看所有群聊列表
python -c "
from src.wechat_client import WeChatAPIClient
client = WeChatAPIClient()
rooms = client.get_chat_rooms(limit=50)
for room in rooms:
    print(f'{room[\"name\"]} - {room[\"nickName\"]}')
"
```

### 3. 思源笔记连接失败
- 检查思源笔记是否在运行
- 确认API端口6806是否开放
- 验证笔记本ID和Auth Token是否正确
- 检查网络连接是否正常

### 4. 邮件发送失败
- 检查SMTP配置是否正确
- 确保使用应用专用密码（而非账户密码）
- 确认防火墙未阻止SMTP端口

### 5. AI服务错误
- **OpenAI**: 检查API密钥和额度
- **Gemini**: 确认API密钥有效且未超限额
- **本地模式**: 无需额外配置

### 6. 查看日志
```bash
# 查看应用日志
tail -f logs/wechat_reporter_$(date +%Y%m%d).log

# 查看cron日志
tail -f logs/cron.log
```

## 📋 系统要求

- **操作系统**: Linux, macOS, Windows
- **Python**: 3.8+
- **内存**: 最少512MB
- **存储**: 最少100MB可用空间
- **网络**: 需要访问AI服务API（如使用OpenAI或Gemini）

## 🔒 安全注意事项

1. **配置文件安全**: `.env`文件包含敏感信息，请勿提交到版本控制
2. **API密钥保护**: 妥善保管OpenAI、Gemini等API密钥
3. **网络安全**: 确保微信API服务仅在本地网络可访问
4. **思源笔记安全**: 保护好思源笔记的API Token
5. **日志审计**: 定期检查和清理日志文件

## 🎯 高级用法

### 自定义AI提示词

可以修改`src/summarizer.py`中的`_build_prompt`方法来自定义AI分析逻辑：

```python
def _build_prompt(self, group_name: str, formatted_messages: str) -> str:
    return f"""
    自定义的提示词内容...
    请分析群聊 '{group_name}' 的聊天记录...
    """
```

### 批量处理历史数据

```bash
# 生成过去一周的报告
for i in {1..7}; do
    date=$(date -d "$i days ago" +%Y-%m-%d)
    python main.py --date $date
done
```

### 集成其他服务

可以扩展`NotificationService`类来支持更多通知方式：
- 钉钉机器人
- 企业微信
- Slack
- Discord等

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 贡献指南
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 支持

如有问题或建议，请创建Issue进行反馈。

### 常见问题
- 查看[Issues页面](../../issues)获取常见问题解答
- 参考[Wiki文档](../../wiki)获取更多使用技巧
- 加入讨论组交流使用经验

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！