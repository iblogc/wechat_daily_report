#!/usr/bin/env python3
"""
测试 Resend 邮件发送功能
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.report_generator import NotificationService

def test_resend_email():
    """测试 Resend 邮件发送"""
    
    # 检查必要的环境变量
    resend_api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('RESEND_FROM_EMAIL')
    to_email = os.getenv('NOTIFICATION_EMAIL')
    
    if not resend_api_key:
        print("❌ RESEND_API_KEY not configured")
        return False
    
    if not from_email:
        print("❌ RESEND_FROM_EMAIL not configured")
        return False
    
    if not to_email:
        print("❌ NOTIFICATION_EMAIL not configured")
        return False
    
    print("📧 Testing Resend email functionality...")
    print(f"   API Key: {resend_api_key[:10]}...")
    print(f"   From: {from_email}")
    print(f"   To: {to_email}")
    
    # 创建通知服务
    resend_config = {
        'api_key': resend_api_key,
        'from_email': from_email
    }
    
    notification_service = NotificationService(resend_config=resend_config)
    
    # 创建测试报告内容
    test_report = """# 微信群聊每日报告测试

**报告日期**: 2025-07-16  
**生成时间**: 2025-07-16 15:30:00  
**监控群数**: 2  
**消息总数**: 150

---

## 📊 群聊概况
- **群聊名称**: 测试群聊
- **活跃成员**: 5人
- **消息总数**: 75条
- **时间跨度**: 2025-07-15 05:00 ~ 2025-07-16 05:00

## 🔥 核心话题

1. **功能测试**: 
   - 核心内容: 测试 Resend 邮件发送功能
   - 主要观点: 邮件发送应该稳定可靠
   - 参与讨论: 开发团队

## 💡 有价值信息
- **重要通知**: Resend 邮件功能已集成
- **技术改进**: 使用 HTML 格式提升邮件阅读体验

---

*本报告由微信聊天记录自动分析系统生成*
"""
    
    # 发送测试邮件
    try:
        success = notification_service.send_email_report(
            report_content=test_report,
            report_date="2025-07-16",
            recipient_email=to_email
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("📬 Please check your inbox for the test report")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    success = test_resend_email()
    sys.exit(0 if success else 1)