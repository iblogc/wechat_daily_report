# 微信群聊记录导出工具使用说明

这是一个独立的聊天记录导出脚本，用于导出指定群聊在指定日期范围内的聊天记录，并按照格式化方式整理成 Markdown 文件。

## ✅ 功能特点

### 🔧 **独立运行**

- 不依赖配置文件，所有参数通过命令行指定
- 可以独立于主项目运行
- 使用与 `summarizer.py` 相同的消息格式化方法

### 📅 **灵活的日期支持**

- 支持单日导出：`--date 2025-01-15`
- 支持日期范围：`--start-date 2025-01-01 --end-date 2025-01-07`
- 支持范围格式：`--date 2025-01-01:2025-01-07`

### 📁 **按群聊组织**

- 每个群聊生成一个独立的 Markdown 文件
- 文件名格式：`群聊名称_日期范围.md`
- 自动处理文件名中的特殊字符

### 👤 **消息标识**

- 自动标识自己发送的消息 `[我]`
- 支持引用消息的标识
- 完整保留消息格式和时间信息

### 🔄 **智能处理**

- 自动跳过图片等非文本消息
- 支持链接分享消息的格式化
- 支持引用回复消息的层级显示
- 自动清理和格式化时间戳

## 📋 使用方法

### 基本用法

```bash
# 导出单日记录
python export_chat_logs.py --group "技术交流群" --date 2025-01-15

# 导出日期范围记录
python export_chat_logs.py --group "技术交流群" --start-date 2025-01-01 --end-date 2025-01-07

# 使用日期范围格式
python export_chat_logs.py --group "技术交流群" --date 2025-01-01:2025-01-07
```

### 高级用法

```bash
# 指定输出目录
python export_chat_logs.py --group "技术交流群" --date 2025-01-15 --output exports/

# 指定API地址
python export_chat_logs.py --group "技术交流群" --date 2025-01-15 --api-url http://127.0.0.1:5030

# 调整请求参数
python export_chat_logs.py --group "技术交流群" --date 2025-01-15 --limit 2000 --timeout 60

# 批量导出多个群聊
python export_chat_logs.py --group "技术交流群" --date 2025-01-15
python export_chat_logs.py --group "产品讨论组" --date 2025-01-15
python export_chat_logs.py --group "项目管理群" --date 2025-01-15
```

### 查看帮助

```bash
python export_chat_logs.py --help
```

## 🔧 命令行参数详解

| 参数           | 简写 | 必需 | 默认值                  | 说明                                                 |
| -------------- | ---- | ---- | ----------------------- | ---------------------------------------------------- |
| `--group`      | `-g` | ✅   | -                       | 群聊名称或群聊 ID                                    |
| `--date`       | `-d` | ✅\* | -                       | 日期或日期范围 (YYYY-MM-DD 或 YYYY-MM-DD:YYYY-MM-DD) |
| `--start-date` | -    | ✅\* | -                       | 开始日期 (YYYY-MM-DD)                                |
| `--end-date`   | -    | -    | -                       | 结束日期 (YYYY-MM-DD，与--start-date 配合使用)       |
| `--output`     | `-o` | -    | `exports`               | 输出目录                                             |
| `--api-url`    | -    | -    | `http://127.0.0.1:5030` | 微信 API 地址                                        |
| `--limit`      | -    | -    | `1000`                  | 每次请求的消息数量限制                               |
| `--timeout`    | -    | -    | `30`                    | API 请求超时时间(秒)                                 |

**注意**：`--date` 和 `--start-date` 二选一，不能同时使用。

### 日期格式说明

- **单日格式**：`2025-01-15`
- **日期范围格式 1**：`--start-date 2025-01-01 --end-date 2025-01-07`
- **日期范围格式 2**：`--date 2025-01-01:2025-01-07`
- **自然日**：按自然日计算，从 00:00:00 到 23:59:59

## 📊 输出格式示例

生成的 Markdown 文件包含以下结构：

```markdown
# 技术交流群 - 聊天记录

**导出日期范围**: 2025-01-15  
**导出时间**: 2025-01-15 14:30:25  
**参与人数**: 8 人  
**消息总数**: 156 条

## 参与成员

张三, 李四, 王五, 赵六, 钱七, 孙八

## 聊天记录
```

[01-15 09:00] 张三 [我]: 早上好大家
[01-15 09:01] 李四: 早上好！
[01-15 09:02] 王五: 今天有什么安排吗？
[01-15 09:03] 张三 [我]: 我们来讨论一下新项目
└ 回复 王五: 今天有什么安排吗？
[01-15 09:04] 李四: [分享] [项目文档](https://example.com/doc)
[01-15 09:05] 赵六: 收到，我看看
[01-15 09:10] 钱七: 这个方案不错
[01-15 09:15] 孙八: 我有一些建议

```

---

*本记录由微信聊天记录导出工具生成*
```

## 📁 输出文件结构

```
exports/
├── 技术交流群_2025-01-15.md                    # 单日记录
├── 产品讨论组_2025-01-01_to_2025-01-07.md      # 日期范围记录
├── 项目管理群_2025-01-15.md
└── 客户服务群_2025-01-10_to_2025-01-15.md
```

### 文件命名规则

- **单日记录**：`群聊名称_YYYY-MM-DD.md`
- **日期范围**：`群聊名称_YYYY-MM-DD_to_YYYY-MM-DD.md`
- **特殊字符处理**：自动将文件名中的特殊字符替换为下划线
- **长度限制**：群聊名称超过 50 个字符时会被截断

## 🚀 使用场景

### 1. 单群聊单日导出

```bash
# 导出技术交流群2025年1月15日的聊天记录
python export_chat_logs.py --group "技术交流群" --date 2025-01-15
```

### 2. 单群聊多日导出

```bash
# 导出技术交流群一周的聊天记录
python export_chat_logs.py --group "技术交流群" --date 2025-01-01:2025-01-07
```

### 3. 批量导出多个群聊

```bash
#!/bin/bash
# 批量导出脚本示例

groups=("技术交流群" "产品讨论组" "项目管理群" "客户服务群")
date="2025-01-15"

for group in "${groups[@]}"; do
    echo "正在导出: $group"
    python export_chat_logs.py --group "$group" --date "$date"
done

echo "批量导出完成！"
```

### 4. 历史数据导出

```bash
# 导出过去一个月的记录
python export_chat_logs.py --group "技术交流群" --date 2024-12-15:2025-01-15
```

## ⚠️ 注意事项

### 1. API 服务要求

- 确保微信聊天记录 API 服务正在运行
- 默认地址：`http://127.0.0.1:5030`
- 如果使用不同地址，请通过 `--api-url` 参数指定

### 2. 群聊名称

- 使用群聊的显示名称，不是群聊 ID
- 如果群聊名称包含特殊字符，请用引号包围
- 群聊名称必须与 API 中的名称完全匹配

### 3. 日期范围

- 使用 `YYYY-MM-DD` 格式
- 开始日期不能晚于结束日期
- 日期范围过大可能导致请求时间较长

### 4. 性能考虑

- 大量消息可能需要较长时间处理
- 可以通过 `--limit` 参数调整每次请求的消息数量
- 可以通过 `--timeout` 参数调整请求超时时间

## 🔍 故障排除

### 1. API 连接失败

```bash
# 检查API服务是否运行
curl http://127.0.0.1:5030/api/v1/session?format=json&limit=1

# 如果使用不同端口
python export_chat_logs.py --group "群聊名称" --date 2025-01-15 --api-url http://127.0.0.1:其他端口
```

### 2. 找不到群聊

```bash
# 检查群聊名称是否正确
curl "http://127.0.0.1:5030/api/v1/chatroom?format=json&limit=50"
```

### 3. 没有聊天记录

- 检查日期范围是否正确
- 确认该时间段内群聊确实有消息
- 检查群聊名称是否准确

### 4. 文件保存失败

- 检查输出目录是否有写入权限
- 确认磁盘空间充足
- 检查文件名是否包含非法字符

## 📝 输出内容说明

### 消息格式化规则

1. **时间格式**：`[MM-DD HH:MM]` (月-日 时:分)
2. **发送者标识**：
   - 自己发送：`张三 [我]`
   - 他人发送：`李四`
3. **消息类型**：
   - 文本消息：直接显示内容
   - 链接分享：`[分享] [标题](链接)`
   - 引用回复：显示原消息和回复内容
   - 图片消息：跳过不显示
4. **引用消息格式**：
   ```
   [01-15 09:03] 张三 [我]: 我们来讨论一下新项目
     └ 回复 王五: 今天有什么安排吗？
   ```

### 统计信息

- **参与人数**：统计发送过消息的用户数量
- **消息总数**：统计有效文本消息数量（不包括图片等）
- **参与成员**：按字母顺序列出所有发言用户

## 🔄 与主项目的关系

这个导出工具是完全独立的，但与主项目共享以下特性：

- **相同的消息格式化逻辑**：使用与 `summarizer.py` 相同的格式化方法
- **相同的 API 接口**：使用相同的微信 API 服务
- **一致的时间处理**：使用相同的时间格式和处理逻辑
- **相同的消息类型支持**：支持文本、链接、引用等消息类型

但导出工具有以下区别：

- **不需要 AI 服务**：纯文本导出，无需配置 AI API
- **不需要配置文件**：所有参数通过命令行指定
- **专注于原始数据**：导出完整的聊天记录，不进行 AI 分析
- **灵活的日期范围**：支持任意日期范围的导出

---

💡 **提示**：这个工具可以作为数据备份、历史查看、或为其他分析工具提供数据源的有用工具。
