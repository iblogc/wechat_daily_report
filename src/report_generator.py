"""
Report Generator for WeChat Daily Reports
"""
from datetime import datetime
from typing import List, Dict
import os
import logging
from jinja2 import Template


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_report(self, summaries: List[Dict], report_date: str = None) -> str:
        """
        生成每日报告
        
        Args:
            summaries: 各群聊总结列表，格式：[{'group_name': str, 'summary': str, 'message_count': int}]
            report_date: 报告日期，默认为昨天
        """
        if not report_date:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        # 统计总体信息
        total_groups = len(summaries)
        total_messages = sum(s.get('message_count', 0) for s in summaries)
        
        # 构建报告内容
        report_data = {
            'report_date': report_date,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_groups': total_groups,
            'total_messages': total_messages,
            'summaries': summaries
        }
        
        # 使用模板生成报告
        template_content = self._get_template_content()
        template = Template(template_content)
        
        return template.render(**report_data)
    
    def save_report(self, content: str, report_date: str = None, 
                   output_dir: str = None) -> str:
        """
        保存报告到文件
        
        Returns:
            str: 保存的文件路径
        """
        if not report_date:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"wechat_daily_report_{report_date}.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Report saved to: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            raise
    
    def _get_template_content(self) -> str:
        """获取报告模板内容"""
        template_path = os.path.join(self.template_dir, 'daily_report.md')
        
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.warning(f"Failed to read template file: {e}")
        
        # 使用默认模板
        return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """默认报告模板"""
        return """# 微信群聊每日报告

**报告日期**: {{ report_date }}  
**生成时间**: {{ generation_time }}  
**监控群数**: {{ total_groups }}  
**消息总数**: {{ total_messages }}

---

{% for summary in summaries %}
{% if summary.summary %}
{{ summary.summary }}

{% if not loop.last %}---{% endif %}

{% endif %}
{% endfor %}

---

*本报告由微信聊天记录自动分析系统生成*
"""


class NotificationService:
    """通知服务"""
    
    def __init__(self, smtp_config: Dict = None, siyuan_config: Dict = None):
        self.smtp_config = smtp_config or {}
        self.siyuan_config = siyuan_config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化思源笔记客户端
        if self.siyuan_config.get('enabled'):
            from .siyuan_client import SiYuanNotesClient
            self.siyuan_client = SiYuanNotesClient(
                base_url=self.siyuan_config.get('base_url', 'http://127.0.0.1:6806'),
                notebook_id=self.siyuan_config.get('notebook_id', '20250207155248-so9nz4m'),
                auth_token=self.siyuan_config.get('auth_token')
            )
        else:
            self.siyuan_client = None
    
    def send_email_report(self, report_content: str, report_date: str, 
                         recipient_email: str) -> bool:
        """
        发送邮件报告
        
        Args:
            report_content: 报告内容
            report_date: 报告日期  
            recipient_email: 收件人邮箱
            
        Returns:
            bool: 发送是否成功
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = Header(self.smtp_config.get('user', ''), 'utf-8')
            msg['To'] = Header(recipient_email, 'utf-8')
            msg['Subject'] = Header(f'微信群聊每日报告 - {report_date}', 'utf-8')
            
            # 添加邮件正文
            text_content = MIMEText(report_content, 'plain', 'utf-8')
            msg.attach(text_content)
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_config.get('server'), 
                                self.smtp_config.get('port', 587))
            server.starttls()
            server.login(self.smtp_config.get('user'), 
                        self.smtp_config.get('password'))
            
            text = msg.as_string()
            server.sendmail(self.smtp_config.get('user'), recipient_email, text)
            server.quit()
            
            self.logger.info(f"Email report sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def save_to_siyuan(self, report_content: str, report_date: str, 
                      group_summaries: List[Dict] = None) -> bool:
        """
        保存报告到思源笔记
        
        Args:
            report_content: 报告内容
            report_date: 报告日期
            group_summaries: 各群聊总结列表
            
        Returns:
            bool: 保存是否成功
        """
        if not self.siyuan_client:
            self.logger.warning("SiYuan client not configured")
            return False
        
        try:
            # 保存每日总报告
            success = self.siyuan_client.save_daily_report(
                report_content, report_date, group_summaries
            )
            
            if success:
                self.logger.info(f"Report saved to SiYuan successfully for {report_date}")
                
                # 如果配置了详细模式，也保存各群聊的单独报告
                if self.siyuan_config.get('save_individual_groups', False) and group_summaries:
                    for summary in group_summaries:
                        if summary.get('summary'):
                            self.siyuan_client.save_group_report(
                                summary['group_name'],
                                summary['summary'],
                                report_date
                            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to save to SiYuan: {e}")
            return False
    
    def send_report(self, report_content: str, report_date: str, 
                   method: str = "email", **kwargs) -> bool:
        """
        发送报告
        
        Args:
            report_content: 报告内容
            report_date: 报告日期
            method: 发送方式 (email, console, file, siyuan)
            **kwargs: 其他参数
        """
        if method == "email":
            recipient = kwargs.get('recipient_email')
            if not recipient:
                self.logger.error("Email recipient not specified")
                return False
            return self.send_email_report(report_content, report_date, recipient)
        
        elif method == "console":
            print("\n" + "="*60)
            print(f"微信群聊每日报告 - {report_date}")
            print("="*60)
            print(report_content)
            print("="*60)
            return True
        
        elif method == "file":
            # 报告已经在ReportGenerator中保存了
            return True
        
        elif method == "siyuan":
            group_summaries = kwargs.get('group_summaries', [])
            return self.save_to_siyuan(report_content, report_date, group_summaries)
        
        else:
            self.logger.error(f"Unsupported notification method: {method}")
            return False