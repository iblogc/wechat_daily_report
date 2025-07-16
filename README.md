# 微信群聊每日报告生成器

这是一个自动化的微信群聊记录分析工具，可以每天自动拉取指定群聊的聊天记录，使用AI进行智能总结，并生成结构化的日报发送给用户。

## 🌟 功能特点

- 🤖 **智能总结**: 支持OpenAI GPT、Google Gemini等AI服务对聊天记录进行智能分析和总结
- 📱 **多群监控**: 可同时监控多个微信群聊
- ⏰ **自动化运行**: 支持cron和systemd定时任务，每天自动生成报告
- 📧 **专业邮件服务**: 使用Resend服务发送HTML格式的精美邮件报告
- 🔧 **灵活配置**: 支持本地简单总结和AI智能总结两种模式
- 📊 **结构化报告**: 生成包含群聊活跃度、核心话题、FAQ、待跟进事项等的结构化报告
- 📓 **思源笔记集成**: 自动保存报告到思源笔记，支持结构化存储和标签管理
- 🌐 **智能代理管理**: 支持代理设置，在AI请求时自动启用，完成后自动清理
- 🔍 **全面连接测试**: 一键测试微信API、AI服务、思源笔记、邮件服务等所有连接状态
- ⏰ **优化时间范围**: 报告覆盖前一天5点到当天5点，更符合实际聊天习惯
- 🎨 **美观邮件**: 自动将Markdown报告转换为带样式的HTML邮件

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
│   ├── siyuan_client.py   # 思源笔记客户端
│   └── proxy_manager.py   # 代理管理器
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
TARGET_GROUPS=your_group_name_1,your_group_name_2

# AI服务设置
AI_SERVICE=gemini  # 可选: openai, gemini, local
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# 邮件通知设置 (使用 Resend)
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAIL=your_email@example.com

# 思源笔记集成
SIYUAN_ENABLED=true
SIYUAN_BASE_URL=http://127.0.0.1:6806
SIYUAN_NOTEBOOK_ID=your_notebook_id
SIYUAN_AUTH_TOKEN=your_siyuan_token
SIYUAN_SAVE_INDIVIDUAL_GROUPS=true

# 报告设置
MAX_MESSAGES_PER_GROUP=200

# 代理设置
PROXY_ENABLED=false
PROXY_HTTP=http://127.0.0.1:7890
PROXY_HTTPS=http://127.0.0.1:7890
```

### 4. 测试运行

```bash
# 🔍 全面连接测试（推荐首次运行）
python main.py --test

# 手动生成报告
python main.py

# 生成指定日期的报告
python main.py --date 2023-12-01
```

**连接测试功能**：
- ✅ **微信API连接**: 测试chatlog服务可用性，显示可用群聊列表
- 🤖 **AI服务测试**: 使用models API检测AI服务连接状态和模型可用性
- 📓 **思源笔记连接**: 验证思源笔记API连接和权限
- 📧 **邮件配置检查**: 确认SMTP配置是否完整
- 🌐 **代理状态显示**: 显示代理配置和使用状态

**时间范围说明**：
- 📅 **报告覆盖时间**: 前一天5:00 到当天5:00（24小时）
- 🌙 **适应聊天习惯**: 覆盖深夜到凌晨的完整聊天周期
- 📊 **示例**: 2025-07-15的报告覆盖 2025-07-14 05:00 ~ 2025-07-15 05:00

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
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini  # 或 gpt-4
```

#### 2. Google Gemini模式 (推荐)
```bash
AI_SERVICE=gemini
GEMINI_API_KEY=your_gemini_api_key
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
- 群聊昵称：`your_group_name`
- 群聊ID：`your_group_id@chatroom`

### 思源笔记集成

**功能特点**：
- 🗂️ **优化目录结构**：日报扁平化存储 (`/微信群聊日报/2024-01-15-日报`)
- 📁 **群聊分类存储**：按群聊名称分文件夹 (`/微信群聊日报/群聊报告/示例群聊/2024-01-15.md`)
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
SIYUAN_NOTEBOOK_ID=your_notebook_id
SIYUAN_AUTH_TOKEN=your_siyuan_token
SIYUAN_SAVE_INDIVIDUAL_GROUPS=true  # 是否为每个群聊创建单独文档
```

### 代理设置配置

**🌐 智能代理管理**：程序会在AI请求前自动设置代理，请求完成后自动清理代理环境变量，确保不影响其他网络请求。

#### 配置方法

```bash
# 启用代理
PROXY_ENABLED=true
PROXY_HTTP=http://127.0.0.1:7890
PROXY_HTTPS=http://127.0.0.1:7890
```

#### 支持的代理类型

- **HTTP代理**: 适用于OpenAI API请求
- **HTTPS代理**: 适用于Gemini API请求
- **SOCKS代理**: 支持socks5://格式

#### 使用场景

- 🚀 **海外AI服务访问**: 当需要访问OpenAI、Gemini等海外AI服务时
- 🔒 **企业网络环境**: 在有网络限制的企业环境中使用
- ⚡ **网络优化**: 通过代理服务器优化网络连接速度

#### 代理配置示例

```bash
# 常见代理配置
PROXY_ENABLED=true
PROXY_HTTP=http://127.0.0.1:7890    # Clash代理
PROXY_HTTPS=http://127.0.0.1:7890

# 或者使用SOCKS5代理
PROXY_HTTP=socks5://127.0.0.1:1080
PROXY_HTTPS=socks5://127.0.0.1:1080

# 带认证的代理
PROXY_HTTP=http://user:pass@host:port
PROXY_HTTPS=http://user:pass@host:port
```

#### 工作原理

1. **自动管理**: 程序启动时读取代理配置
2. **按需设置**: 仅在AI请求时临时设置代理环境变量
3. **自动清理**: AI请求完成后立即恢复原始环境变量
4. **不影响其他**: 不会影响微信API、邮件发送等其他网络请求

#### 注意事项

- ⚠️ **仅影响AI请求**: 代理设置只对OpenAI和Gemini API生效
- 🔧 **环境变量管理**: 使用上下文管理器确保环境变量正确恢复
- 📝 **日志记录**: 代理的启用和关闭会记录在日志中
- 🚫 **定时任务简化**: 移除了定时任务脚本中的代理设置，统一通过配置文件管理

### 邮件通知配置

使用 **Resend** 服务发送邮件，更稳定可靠：

```bash
# Resend 配置示例
RESEND_API_KEY=re_your_api_key
RESEND_FROM_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAIL=your_email@example.com
```

**Resend 设置步骤**：
1. 访问 [Resend.com](https://resend.com) 注册账户
2. 在控制台创建 API Key
3. 验证发件人域名或使用测试域名
4. 配置环境变量

**Resend 优势**：
- 🚀 **高送达率**: 专业的邮件发送服务
- 📊 **详细统计**: 提供邮件发送状态和统计
- 🔒 **安全可靠**: 无需暴露个人邮箱密码
- 💰 **免费额度**: 每月3000封免费邮件
- 🎨 **HTML支持**: 自动将Markdown转换为美观的HTML邮件

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
- **群聊名称**: 示例讨论群
- **活跃成员**: 12人
- **消息总数**: 156条
- **时间跨度**: 2024-01-15 09:00 ~ 18:30

## 🔥 核心话题

1. **新版本功能规划**: 
   - 核心内容: 讨论V2.0版本的核心功能点
   - 主要观点: 优先级应该放在用户体验优化上
   - 参与讨论: 用户A、用户B、用户C

## ❓ FAQ 常见问题

**Q1**: 新功能什么时候上线？
**A1**: 预计下个月底完成开发，下下个月初发布

## 🎯 待跟进事项
- [ ] 确认UI设计方案 (用户A负责)
- [ ] 制定测试计划 (用户B负责)
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