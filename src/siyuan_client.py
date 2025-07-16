"""
SiYuan Notes API Client for saving reports
"""
import requests
import json
from datetime import datetime
from typing import Dict, Optional
import logging


class SiYuanNotesClient:
    """思源笔记API客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:6806", 
                 notebook_id: str = "20250207155248-so9nz4m", 
                 auth_token: str = None,
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.notebook_id = notebook_id
        self.auth_token = auth_token
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        # 如果提供了认证token，添加到请求头
        if self.auth_token:
            self.session.headers.update({
                'Authorization': f'Token {self.auth_token}'
            })
            
        self.logger = logging.getLogger(__name__)
    
    def create_document_with_markdown(self, path: str, markdown_content: str) -> bool:
        """
        在思源笔记中创建文档
        
        Args:
            path: 文档路径，如 "/微信群聊日报/2024-01-01"
            markdown_content: Markdown内容
            
        Returns:
            bool: 创建是否成功
        """
        url = f"{self.base_url}/api/filetree/createDocWithMd"
        
        payload = {
            "notebook": self.notebook_id,
            "path": path,
            "markdown": markdown_content
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                self.logger.info(f"Successfully created document: {path}")
                return True
            else:
                self.logger.error(f"Failed to create document: {result.get('msg', 'Unknown error')}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Error creating document in SiYuan: {e}")
            return False
    
    def save_daily_report(self, report_content: str, report_date: str, 
                         group_summaries: list = None) -> bool:
        """
        保存每日报告到思源笔记
        
        Args:
            report_content: 完整报告内容
            report_date: 报告日期 (YYYY-MM-DD)
            group_summaries: 各群聊总结列表
            
        Returns:
            bool: 保存是否成功
        """
        # 优化文档路径 - 减少层级深度
        # 旧格式：/微信群聊日报/2024/01/2024-01-15-微信群聊日报
        # 新格式：/微信群聊日报/2024-01-15-日报
        doc_path = f"/微信群聊日报/{report_date}-日报"
        
        # 优化报告内容格式
        formatted_content = self._format_report_for_siyuan(
            report_content, report_date, group_summaries
        )
        
        return self.create_document_with_markdown(doc_path, formatted_content)
    
    def save_group_report(self, group_name: str, summary_content: str, 
                         report_date: str) -> bool:
        """
        保存单个群聊报告到思源笔记
        
        Args:
            group_name: 群聊名称
            summary_content: 群聊总结内容
            report_date: 报告日期
            
        Returns:
            bool: 保存是否成功
        """
        # 清理群名中的特殊字符
        safe_group_name = self._sanitize_filename(group_name)
        
        # 优化文档路径 - 以群名为文件夹，日期为文件名
        # 新格式：/微信群聊日报/群聊报告/群名/YYYY-MM-DD
        doc_path = f"/微信群聊日报/群聊报告/{safe_group_name}/{report_date}"
        
        # 添加标题和元数据
        formatted_content = f"""# {group_name} - {report_date}

> 📅 日期: {report_date}  
> 🕐 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 📱 群聊: {group_name}

{summary_content}

---
*本报告由微信聊天记录自动分析系统生成*
"""
        
        return self.create_document_with_markdown(doc_path, formatted_content)
    
    def _format_report_for_siyuan(self, report_content: str, report_date: str, 
                                 group_summaries: list = None) -> str:
        """格式化报告内容以适配思源笔记"""
        
        # 添加思源笔记友好的元数据和格式
        formatted = f"""# 微信群聊日报 - {report_date}

> 📅 报告日期: {report_date}  
> 🕐 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 🤖 分析引擎: AI智能总结

{report_content}

## 📊 数据统计

"""
        
        if group_summaries:
            formatted += "| 群聊名称 | 消息数量 | 状态 |\n"
            formatted += "|----------|----------|------|\n"
            
            for summary in group_summaries:
                group_name = summary.get('group_name', '未知群聊')
                message_count = summary.get('message_count', 0)
                status = "✅ 已分析" if summary.get('summary') else "⚠️ 无数据"
                formatted += f"| {group_name} | {message_count} | {status} |\n"
        
        formatted += f"""

## 🔗 相关链接

- [微信聊天记录分析系统](file:///)
- [每日报告存档](file:///)

---

**标签**: #微信群聊 #日报 #{report_date.replace('-', '')} #AI分析

*本文档由微信聊天记录自动分析系统生成，保存于思源笔记*
"""
        
        return formatted
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的特殊字符"""
        # 移除或替换文件名中不允许的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 移除emoji等特殊字符，保留中文、英文、数字
        import re
        filename = re.sub(r'[^\w\s\u4e00-\u9fff-]', '_', filename)
        
        # 移除多余的下划线和空格
        filename = re.sub(r'[_\s]+', '_', filename).strip('_')
        
        return filename[:50]  # 限制长度
    
    def test_connection(self) -> bool:
        """测试思源笔记连接"""
        try:
            url = f"{self.base_url}/api/system/getConf"
            response = self.session.post(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False