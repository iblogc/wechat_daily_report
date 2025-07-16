# 微信群聊每日报告

**📅 报告日期**: {{ report_date }}  
**⏰ 生成时间**: {{ generation_time }}  
**👥 监控群数**: {{ total_groups }}  
**💬 消息总数**: {{ total_messages }}

---

{% for summary in summaries %}
{% if summary.summary %}
{{ summary.summary }}

{% if not loop.last %}

---

{% endif %}
{% endif %}
{% endfor %}

---

> 🤖 *本报告由微信聊天记录自动分析系统生成*  
> 📊 *数据来源: 本地微信聊天记录*  
> 🔒 *隐私保护: 所有数据均在本地处理*