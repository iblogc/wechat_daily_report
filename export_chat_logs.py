#!/usr/bin/env python3
"""
微信群聊记录导出工具

独立脚本，用于导出指定群聊在指定日期范围内的聊天记录，
并按照格式化方式整理成Markdown文件。

使用方法:
python export_chat_logs.py --group "群聊名称" --start-date 2025-01-01 --end-date 2025-01-07
python export_chat_logs.py --group "群聊名称" --date 2025-01-01  # 单日导出
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wechat_client import WeChatAPIClient


class ChatLogExporter:
    """聊天记录导出器"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5030", timeout: int = 30):
        self.api_base_url = api_base_url.rstrip('/')
        self.timeout = timeout
        self.logger = self._setup_logger()
        # 使用现有的WeChatAPIClient
        self.api_client = WeChatAPIClient(base_url=api_base_url, timeout=timeout)
    
    def _setup_logger(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def get_chat_logs(self, group_name: str, start_date: str, end_date: str, limit: int = 1000) -> List[Dict]:
        """
        获取指定群聊在日期范围内的聊天记录
        
        Args:
            group_name: 群聊名称
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 每次请求的消息数量限制
            
        Returns:
            List[Dict]: 聊天记录列表
        """
        self.logger.info(f"获取群聊 '{group_name}' 从 {start_date} 到 {end_date} 的聊天记录")
        
        # 构建时间范围字符串，格式为 "start_date~end_date"
        if start_date == end_date:
            time_range = start_date
        else:
            time_range = f"{start_date}~{end_date}"
        
        all_logs = []
        offset = 0
        
        while True:
            try:
                # 使用WeChatAPIClient的get_chat_logs方法
                response_data = self.api_client.get_chat_logs(
                    talker=group_name,
                    time_range=time_range,
                    limit=limit,
                    offset=offset
                )
                
                # 检查响应数据格式
                if isinstance(response_data, dict):
                    logs = response_data.get('data', [])
                elif isinstance(response_data, list):
                    logs = response_data
                else:
                    self.logger.error(f"意外的响应格式: {type(response_data)}")
                    break
                
                if not logs:
                    break
                
                all_logs.extend(logs)
                self.logger.info(f"已获取 {len(all_logs)} 条消息")
                
                # 如果返回的消息数量少于limit，说明已经获取完所有消息
                if len(logs) < limit:
                    break
                
                offset += limit
                
            except Exception as e:
                self.logger.error(f"获取聊天记录时出错: {e}")
                break
        
        self.logger.info(f"总共获取到 {len(all_logs)} 条消息")
        return all_logs
    
    def format_messages(self, chat_logs: List[Dict]) -> str:
        """
        格式化聊天消息 - 与summarizer.py中的方法保持一致
        """
        messages = []
        for log in chat_logs:
            time_str = log.get('time', '')
            sender = log.get('senderName', '未知用户')
            content = log.get('content', '')
            msg_type = log.get('type', 0)
            contents = log.get('contents', {})
            is_self = log.get('isSelf', False)
            
            # 精简时间格式 (保留月日时分)
            if time_str:
                try:
                    # 从 "2025-07-04T10:05:32+08:00" 提取 "07-04 10:05"
                    date_part = time_str.split('T')[0].split('-')  # ['2025', '07', '04']
                    time_part = time_str.split('T')[1].split('+')[0][:5]  # '10:05'
                    time_str = f"{date_part[0]}-{date_part[1]}-{date_part[2]} {time_part}"
                except:
                    time_str = time_str
            
            # 处理不同类型的消息
            formatted_content = ""
            
            if msg_type == 1:  # 文本消息
                formatted_content = content
            elif msg_type == 3:  # 图片消息 - 跳过不处理
                continue
            elif msg_type == 49:  # 链接/引用消息
                sub_type = log.get('subType', 0)
                if sub_type == 51:  # 链接分享
                    title = contents.get('title', '')
                    url = contents.get('url', '')
                    formatted_content = f"[分享] [{title}]" + (f"({url})" if url else "")
                elif sub_type == 57 and contents.get('refer'):  # 引用消息
                    refer = contents['refer']
                    refer_sender = refer.get('senderName', '未知用户')
                    refer_content = refer.get('content', '')
                    refer_is_self = refer.get('isSelf', False)
                    
                    # 为引用消息的发送者也添加特殊标记
                    refer_sender_display = f"{refer_sender} [我]" if refer_is_self else refer_sender
                    
                    # 处理引用消息，保留完整内容
                    formatted_content = f"{content}\n  └ 回复 {refer_sender_display}: {refer_content}"
                else:
                    formatted_content = content or "[其他消息]"
            else:
                # 其他类型消息，只保留有文本内容的
                if content and content.strip():
                    formatted_content = content
                else:
                    continue  # 跳过无文本内容的消息
            
            # 跳过空消息
            if not formatted_content.strip():
                continue
            
            # 为自己发送的消息添加特殊标记
            sender_display = f"{sender} [我]" if is_self else sender
            messages.append(f"[{time_str}] {sender_display}: {formatted_content}")
        
        return "\n".join(messages)
    
    def generate_markdown_report(self, group_name: str, chat_logs: List[Dict], 
                                start_date: str, end_date: str) -> str:
        """
        生成Markdown格式的聊天记录报告
        
        Args:
            group_name: 群聊名称
            chat_logs: 聊天记录列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            str: Markdown格式的报告内容
        """
        # 格式化消息
        formatted_messages = self.format_messages(chat_logs)
        
        # # 统计信息
        # total_messages = len([log for log in chat_logs if log.get('type') == 1])
        # senders = set()
        # for log in chat_logs:
        #     if log.get('type') == 1:  # 文本消息
        #         sender = log.get('senderName', '未知')
        #         senders.add(sender)
        
        # # 生成报告内容
        # date_range = start_date if start_date == end_date else f"{start_date} 至 {end_date}"
        
        return formatted_messages
        
    def save_report(self, content: str, group_name: str, start_date: str, end_date: str, 
                   output_dir: str = "exports") -> str:
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            group_name: 群聊名称
            start_date: 开始日期
            end_date: 结束日期
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成安全的文件名
        safe_group_name = self._sanitize_filename(group_name)
        date_range = start_date if start_date == end_date else f"{start_date}_to_{end_date}"
        filename = f"{safe_group_name}_{date_range}.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"报告已保存到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全的字符
        """
        import re
        # 移除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除多余的空格和点
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        safe_name = safe_name.strip('.')
        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        return safe_name or 'unknown_group'
    
    def export_chat_logs(self, group_name: str, start_date: str, end_date: str, 
                        output_dir: str = "exports", limit: int = 1000) -> str:
        """
        导出聊天记录的主方法
        
        Args:
            group_name: 群聊名称
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            output_dir: 输出目录
            limit: 每次请求的消息数量限制
            
        Returns:
            str: 保存的文件路径
        """
        # 获取聊天记录
        chat_logs = self.get_chat_logs(group_name, start_date, end_date, limit)
        
        if not chat_logs:
            self.logger.warning(f"未找到群聊 '{group_name}' 在 {start_date} 到 {end_date} 期间的聊天记录")
            return None
        
        # 生成报告
        report_content = self.generate_markdown_report(group_name, chat_logs, start_date, end_date)
        
        # 保存报告
        filepath = self.save_report(report_content, group_name, start_date, end_date, output_dir)
        
        return filepath


def parse_date_range(date_arg: str) -> tuple:
    """
    解析日期参数
    
    Args:
        date_arg: 日期参数，支持单个日期或日期范围
        
    Returns:
        tuple: (start_date, end_date)
    """
    if ':' in date_arg:
        # 日期范围格式: 2025-01-01:2025-01-07
        start_date, end_date = date_arg.split(':', 1)
        start_date = start_date.strip()
        end_date = end_date.strip()
    else:
        # 单个日期
        start_date = end_date = date_arg.strip()
    
    # 验证日期格式
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"日期格式错误，请使用 YYYY-MM-DD 格式: {e}")
    
    # 检查日期范围
    if start_date > end_date:
        raise ValueError("开始日期不能晚于结束日期")
    
    return start_date, end_date


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='微信群聊记录导出工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 导出单日记录
  python export_chat_logs.py --group "技术交流群" --date 2025-01-15
  
  # 导出日期范围记录
  python export_chat_logs.py --group "技术交流群" --start-date 2025-01-01 --end-date 2025-01-07
  
  # 使用日期范围格式
  python export_chat_logs.py --group "技术交流群" --date 2025-01-01:2025-01-07
  
  # 指定输出目录
  python export_chat_logs.py --group "技术交流群" --date 2025-01-15 --output exports/
  
  # 指定API地址
  python export_chat_logs.py --group "技术交流群" --date 2025-01-15 --api-url http://127.0.0.1:5030
        """
    )
    
    # 必需参数
    parser.add_argument('--group', '-g', required=True, help='群聊名称')
    
    # 日期参数（三种方式任选一种）
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument('--date', '-d', help='日期或日期范围 (YYYY-MM-DD 或 YYYY-MM-DD:YYYY-MM-DD)')
    date_group.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    
    # 可选参数
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD，与--start-date配合使用)')
    parser.add_argument('--output', '-o', default='exports', help='输出目录 (默认: exports)')
    parser.add_argument('--api-url', default='http://127.0.0.1:5030', help='微信API地址 (默认: http://127.0.0.1:5030)')
    parser.add_argument('--limit', type=int, default=1000, help='每次请求的消息数量限制 (默认: 1000)')
    parser.add_argument('--timeout', type=int, default=30, help='API请求超时时间(秒) (默认: 30)')
    
    args = parser.parse_args()
    
    try:
        # 解析日期参数
        if args.date:
            start_date, end_date = parse_date_range(args.date)
        elif args.start_date:
            if not args.end_date:
                parser.error("使用 --start-date 时必须同时指定 --end-date")
            start_date, end_date = args.start_date, args.end_date
            # 验证日期格式
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            if start_date > end_date:
                raise ValueError("开始日期不能晚于结束日期")
        
        # 创建导出器
        exporter = ChatLogExporter(api_base_url=args.api_url, timeout=args.timeout)
        
        # 导出聊天记录
        print(f"🚀 开始导出群聊 '{args.group}' 的聊天记录...")
        print(f"📅 日期范围: {start_date} 到 {end_date}")
        print(f"🌐 API地址: {args.api_url}")
        print(f"📁 输出目录: {args.output}")
        print()
        
        filepath = exporter.export_chat_logs(
            group_name=args.group,
            start_date=start_date,
            end_date=end_date,
            output_dir=args.output,
            limit=args.limit
        )
        
        if filepath:
            print(f"✅ 导出完成！")
            print(f"📄 文件路径: {filepath}")
        else:
            print("❌ 导出失败，未找到聊天记录")
            return 1
        
        return 0
        
    except ValueError as e:
        print(f"❌ 参数错误: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())