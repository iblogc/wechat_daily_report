"""
WeChat Daily Report Main Application
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wechat_client import WeChatAPIClient
from src.summarizer import SummarizerFactory
from src.report_generator import ReportGenerator, NotificationService
from src.proxy_manager import ProxyManager


class WeChatDailyReporter:
    """微信每日报告生成器"""
    
    def __init__(self, config_file: str = ".env"):
        # 加载配置
        load_dotenv(config_file)
        self._setup_logging()
        self._load_config()
        
        # 初始化组件
        self.api_client = WeChatAPIClient(
            base_url=self.config['api_base_url'],
            timeout=self.config['api_timeout']
        )
        
        # 创建代理管理器
        self.proxy_manager = ProxyManager.from_config({
            'proxy_enabled': self.config['proxy_enabled'],
            'proxy_http': self.config['proxy_http'],
            'proxy_https': self.config['proxy_https']
        })
        
        # 准备AI服务配置
        api_key = None
        model = None
        
        if self.config['ai_service'] == 'openai':
            api_key = self.config['openai_api_key']
            model = self.config['openai_model']
            if not api_key:
                raise ValueError("OpenAI API key is not configured")
            if not model:
                raise ValueError("OpenAI model is not configured")
        elif self.config['ai_service'] == 'gemini':
            api_key = self.config['gemini_api_key']
            model = self.config['gemini_model']
            if not api_key:
                raise ValueError("Gemini API key is not configured")
            if not model:
                raise ValueError("Gemini model is not configured")
        elif self.config['ai_service'] == 'local':
            # 本地模式不需要API密钥和模型
            pass
        else:
            raise ValueError(f"Unsupported AI service: {self.config['ai_service']}")
        
        self.summarizer = SummarizerFactory.create_summarizer(
            service_type=self.config['ai_service'],
            api_key=api_key,
            model=model,
            proxy_manager=self.proxy_manager
        )
        
        self.report_generator = ReportGenerator()
        self.notification_service = NotificationService(
            resend_config=self.config.get('resend_config'),
            siyuan_config=self.config.get('siyuan_config')
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """设置日志"""
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"wechat_reporter_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self):
        """加载配置"""
        self.config = {
            'api_base_url': os.getenv('WECHAT_API_BASE_URL', 'http://127.0.0.1:5030'),
            'api_timeout': int(os.getenv('WECHAT_API_TIMEOUT', '30')),
            'target_groups': [g.strip() for g in os.getenv('TARGET_GROUPS', '').split(',') if g.strip()],
            'ai_service': os.getenv('AI_SERVICE', 'local'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_model': os.getenv('OPENAI_MODEL'),
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'gemini_model': os.getenv('GEMINI_MODEL'),
            'max_messages_per_group': int(os.getenv('MAX_MESSAGES_PER_GROUP', '200')),
            'notification_email': os.getenv('NOTIFICATION_EMAIL'),
            'proxy_enabled': os.getenv('PROXY_ENABLED', 'false').lower() == 'true',
            'proxy_http': os.getenv('PROXY_HTTP'),
            'proxy_https': os.getenv('PROXY_HTTPS'),
            'resend_config': {
                'api_key': os.getenv('RESEND_API_KEY'),
                'from_email': os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
            } if os.getenv('RESEND_API_KEY') else None,
            'siyuan_config': {
                'enabled': os.getenv('SIYUAN_ENABLED', 'false').lower() == 'true',
                'base_url': os.getenv('SIYUAN_BASE_URL', 'http://127.0.0.1:6806'),
                'notebook_id': os.getenv('SIYUAN_NOTEBOOK_ID', '20250207155248-so9nz4m'),
                'auth_token': os.getenv('SIYUAN_AUTH_TOKEN'),
                'save_individual_groups': os.getenv('SIYUAN_SAVE_INDIVIDUAL_GROUPS', 'false').lower() == 'true'
            }
        }
        
        # 验证必要配置
        if not self.config['target_groups']:
            raise ValueError("TARGET_GROUPS must be configured")
    
    def run_daily_report(self, report_date: str = None) -> str:
        """
        运行每日报告生成
        
        Args:
            report_date: 报告日期，格式 YYYY-MM-DD，默认为昨天
            
        Returns:
            str: 生成的报告文件路径
        """
        if not report_date:
            report_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        self.logger.info(f"Starting daily report generation for {report_date}")
        
        # 检查API服务
        if not self.api_client.health_check():
            raise RuntimeError("WeChat API service is not available")
        
        # 收集各群聊的聊天记录和总结
        summaries = []
        
        for group_name in self.config['target_groups']:
            try:
                self.logger.info(f"Processing group: {group_name}")
                
                # 获取聊天记录（前一天5点到当天5点）
                chat_logs = self.api_client.get_daily_report_chats(
                    talker=group_name,
                    report_date=report_date,
                    limit=self.config['max_messages_per_group']
                )
                
                if not chat_logs:
                    self.logger.warning(f"No chat logs found for group: {group_name}")
                    summaries.append({
                        'group_name': group_name,
                        'summary': f"## 群聊：{group_name}\n\n暂无聊天记录",
                        'message_count': 0
                    })
                    continue
                
                # 生成总结
                try:
                    summary = self.summarizer.summarize_chat_logs(chat_logs, group_name)
                except Exception as ai_error:
                    self.logger.error(f"AI summarization failed for group {group_name}: {ai_error}")
                    raise RuntimeError(f"AI总结失败，停止报告生成流程。群聊 '{group_name}' 错误: {str(ai_error)}")
                
                message_count = len([log for log in chat_logs if log.get('type') == 1])
                
                summaries.append({
                    'group_name': group_name,
                    'summary': summary,
                    'message_count': message_count
                })
                
                self.logger.info(f"Generated summary for {group_name}: {message_count} messages")
                
            except RuntimeError:
                # AI总结错误，直接向上抛出
                raise
            except Exception as e:
                self.logger.error(f"Error processing group {group_name}: {e}")
                # 非AI错误，继续处理其他群组
                summaries.append({
                    'group_name': group_name,
                    'summary': f"## 群聊：{group_name}\n\n处理失败: {str(e)}",
                    'message_count': 0
                })
        
        # 生成报告
        report_content = self.report_generator.generate_daily_report(summaries, report_date)
        report_file = self.report_generator.save_report(report_content, report_date)
        
        # 发送通知
        self._send_notifications(report_content, report_date, summaries)
        
        self.logger.info(f"Daily report completed: {report_file}")
        return report_file
    
    def _send_notifications(self, report_content: str, report_date: str, 
                           summaries: List[Dict] = None):
        """发送通知"""
        try:
            # 控制台输出
            self.notification_service.send_report(
                report_content, report_date, method="console"
            )
            
            # 邮件通知
            if self.config['notification_email'] and self.config['resend_config']:
                self.notification_service.send_report(
                    report_content, report_date, method="email",
                    recipient_email=self.config['notification_email']
                )
            
            # 保存到思源笔记
            if self.config['siyuan_config']['enabled']:
                self.notification_service.send_report(
                    report_content, report_date, method="siyuan",
                    group_summaries=summaries
                )
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")


def main():
    """主入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WeChat Daily Report Generator')
    parser.add_argument('--date', type=str, help='Report date (YYYY-MM-DD), default: yesterday')
    parser.add_argument('--config', type=str, default='.env.prod', help='Config file path')
    parser.add_argument('--test', action='store_true', help='Test API connection')
    
    args = parser.parse_args()
    
    try:
        reporter = WeChatDailyReporter(args.config)
        
        if args.test:
            print("🔍 Running connection tests...\n")
            
            # 测试微信API连接
            print("1. Testing WeChat API connection...")
            if reporter.api_client.health_check():
                print("✅ WeChat API connection successful")
                
                # 测试获取群聊列表
                chat_rooms = reporter.api_client.get_chat_rooms(limit=5)
                print(f"📱 Found {len(chat_rooms)} chat rooms")
                for room in chat_rooms[:3]:
                    print(f"  - {room.get('nickName', room.get('name'))}")
            else:
                print("❌ WeChat API connection failed")
                return 1
            
            print()
            
            # 测试AI服务连接
            print(f"2. Testing AI service ({reporter.config['ai_service']})...")
            if reporter.summarizer.test_connection():
                print(f"✅ {reporter.config['ai_service'].upper()} API connection successful")
                if reporter.config['proxy_enabled']:
                    print(f"🌐 Using proxy: {reporter.config['proxy_http']}")
            else:
                print(f"❌ {reporter.config['ai_service'].upper()} API connection failed")
                if reporter.config['ai_service'] != 'local':
                    return 1
            
            print()
            
            # 测试思源笔记连接
            if reporter.config['siyuan_config']['enabled']:
                print("3. Testing SiYuan Notes connection...")
                if reporter.notification_service.siyuan_client.test_connection():
                    print("✅ SiYuan Notes connection successful")
                else:
                    print("❌ SiYuan Notes connection failed")
            else:
                print("3. SiYuan Notes integration disabled")
            
            print()
            
            # 测试邮件配置
            if reporter.config['resend_config'] and reporter.config['notification_email']:
                print("4. Resend email notification configured ✅")
                print(f"   From: {reporter.config['resend_config']['from_email']}")
                print(f"   To: {reporter.config['notification_email']}")
            else:
                print("4. Resend email notification not configured")
            
            print("\n🎉 All tests completed!")
        else:
            # 生成报告
            report_file = reporter.run_daily_report(args.date)
            print(f"✅ Report generated: {report_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())