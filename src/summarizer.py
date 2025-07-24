"""
AI Summarizer for WeChat chat logs
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging
import os
from openai import OpenAI
import google.generativeai as genai
from .proxy_manager import ProxyManager



class BaseSummarizer(ABC):
    """AI总结器基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """总结聊天记录"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试AI服务连接"""
        pass
    
    def _format_messages(self, chat_logs: List[Dict]) -> str:
        """格式化聊天消息 - 通用实现"""
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
                    date_part = time_str.split('T')[0].split('-')[1:]  # ['07', '04']
                    time_part = time_str.split('T')[1].split('+')[0][:5]  # '10:05'
                    time_str = f"{date_part[0]}-{date_part[1]} {time_part}"
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
    
    def _build_prompt(self, group_name: str, formatted_messages: str) -> str:
        """构建AI提示词 - 通用实现，子类可以重写"""
        return f"""
请分析群聊 '{group_name}' 的聊天记录，重点关注核心话题、有价值的观点和重要信息分享。忽略没有意义的图片链接、表情符号等内容。
分析总结目的是为了让阅读者高效快速的从群聊中吸取学习人价值的内容。
指导原则：
1.  **精准提炼**: 聚焦于真正有价值的讨论、信息和决策，忽略闲聊、表情、重复确认等噪音。
2.  **客观中立**: 严格基于聊天记录进行总结，不添加任何主观臆断或外部信息。
3.  **结构清晰**: 严格按照下方指定的 Markdown 格式输出，确保报告的专业性和可读性。
4.  **信息完整**: 如果是一些有价值、教学类的内容，要把完整内容提取，优化表达后完整保留。

聊天记录：
{formatted_messages}

请按以下格式输出结构化总结，注意内容层级缩进，使用标准的markdown语法（CommonMark），直接输出内容，不要输出解释性文字：

## 📊 群聊概况
- **群聊名称**: {group_name}
- **活跃成员**: [统计发言人数]
- **消息总数**: [统计有效消息数量]
- **时间跨度**: [记录时间范围]

## 🔥 核心话题
[按重要性排序，列出最多 20 个主要讨论话题，每个话题包含关键观点]

**话题一**: 

   - 核心内容: 
   - 主要观点: 
   - 参与讨论: 

**话题二**: 

   - 核心内容: 
   - 主要观点: 
   - 参与讨论: 

## 💡 有价值信息
[提取重要的信息分享、资源推荐、经验总结等]

- **重要通知**: 
- **资源分享**: 
- **经验分享**: 
- **决策事项**: 

## ❓ FAQ 常见问题
[尽可能多的整理群内讨论的有价值的问题和解答，最多 20 个问题]

**Q1**: [问题描述]
**A1**: [解答内容]

**Q2**: [问题描述]
**A2**: [解答内容]

## 📝 备注
[其他值得关注的信息或观察]

---
*本总结基于AI分析生成，如有遗漏请参考原始聊天记录*
"""


class OpenAISummarizer(BaseSummarizer):
    """OpenAI总结器"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", proxy_manager: ProxyManager = None):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.proxy_manager = proxy_manager or ProxyManager()
    
    def test_connection(self) -> bool:
        """测试OpenAI API连接"""
        try:
            with self.proxy_manager.proxy_context():
                # 使用models API来测试连接
                models = self.client.models.list()
                # 检查指定的模型是否可用
                available_models = [model.id for model in models.data]
                if self.model in available_models:
                    self.logger.info(f"OpenAI API connection successful, model {self.model} is available")
                    return True
                else:
                    self.logger.warning(f"OpenAI API connected but model {self.model} not found in available models")
                    return False
        except Exception as e:
            self.logger.error(f"OpenAI API connection failed: {e}")
            return False
    
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """使用OpenAI总结聊天记录"""
        if not chat_logs:
            return f"群聊 '{group_name}' 暂无聊天记录"
        
        # 格式化聊天记录
        formatted_messages = self._format_messages(chat_logs)
        
        # 构建提示词
        prompt = self._build_prompt(group_name, formatted_messages)
        
        try:
            # 使用代理上下文管理器
            with self.proxy_manager.proxy_context():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的聊天记录分析师，善于从群聊记录中提取关键信息并生成简洁有用的总结。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
            
            # 获取AI生成的总结
            ai_summary = response.choices[0].message.content.strip()
            
            # 添加折叠的完整聊天记录
            collapsible_section = f"""

<details>
<summary>📋 完整聊天记录</summary>

```
{formatted_messages}
```

</details>"""
            
            return ai_summary + collapsible_section
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
    



class LocalSummarizer(BaseSummarizer):
    """本地总结器（简单文本处理）"""
    
    def __init__(self):
        super().__init__()
    
    def test_connection(self) -> bool:
        """测试本地总结器（总是可用）"""
        self.logger.info("Local summarizer is always available")
        return True
    
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """使用简单规则总结聊天记录"""
        if not chat_logs:
            return f"群聊 '{group_name}' 暂无聊天记录"
        
        # 统计信息
        total_messages = len([log for log in chat_logs if log.get('type') == 1])
        senders = set()
        keywords = {}
        
        for log in chat_logs:
            if log.get('type') == 1:  # 文本消息
                sender = log.get('senderName', '未知')
                senders.add(sender)
                content = log.get('content', '').lower()
                
                # 简单关键词统计
                common_words = ['会议', '时间', '地点', '明天', '今天', '项目', '工作']
                for word in common_words:
                    if word in content:
                        keywords[word] = keywords.get(word, 0) + 1
        
        # 格式化聊天记录
        formatted_messages = self._format_messages(chat_logs)
        
        # 生成简单总结
        summary = f"""## 群聊总结：{group_name}

### 基本信息
- 参与人数：{len(senders)}人
- 消息总数：{total_messages}条

### 参与成员
{', '.join(list(senders)[:10])}{'...' if len(senders) > 10 else ''}

### 热门关键词
{', '.join([f'{k}({v}次)' for k, v in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]])}

*注：这是简单统计总结，如需详细分析请配置AI服务*
"""
        
        # 添加折叠的完整聊天记录
        collapsible_section = f"""

<details>
<summary>📋 完整聊天记录</summary>

```
{formatted_messages}
```

</details>"""
        
        return summary + collapsible_section


class GeminiSummarizer(BaseSummarizer):
    """Google Gemini总结器"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", proxy_manager: ProxyManager = None):
        super().__init__()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        self.proxy_manager = proxy_manager or ProxyManager()
    
    def test_connection(self) -> bool:
        """测试Gemini API连接"""
        try:
            with self.proxy_manager.proxy_context():
                # 使用list_models API来测试连接
                available_models = []
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        available_models.append(model.name)
                
                # 检查指定的模型是否可用
                model_full_name = f"models/{self.model_name}"
                if model_full_name in available_models:
                    self.logger.info(f"Gemini API connection successful, model {self.model_name} is available")
                    return True
                else:
                    self.logger.warning(f"Gemini API connected but model {self.model_name} not found in available models")
                    return False
        except Exception as e:
            self.logger.error(f"Gemini API connection failed: {e}")
            return False
    
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """使用Google Gemini总结聊天记录"""
        if not chat_logs:
            return f"群聊 '{group_name}' 暂无聊天记录"
        
        # 格式化聊天记录
        formatted_messages = self._format_messages(chat_logs)
        
        # 构建提示词
        prompt = self._build_prompt(group_name, formatted_messages)
        
        try:
            # 使用代理上下文管理器
            with self.proxy_manager.proxy_context():
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3
                    )
                )
            
            # 获取AI生成的总结
            ai_summary = response.text.strip()
            
            # 添加折叠的完整聊天记录
            collapsible_section = f"""

<details>
<summary>📋 完整聊天记录</summary>

```
{formatted_messages}
```

</details>"""
            
            return ai_summary + collapsible_section
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            self.logger.exception(e)
            raise RuntimeError(f"Gemini API调用失败: {str(e)}")
    



class SummarizerFactory:
    """总结器工厂类"""
    
    @staticmethod
    def create_summarizer(service_type: str, **kwargs) -> BaseSummarizer:
        """创建总结器实例"""
        proxy_manager = kwargs.get('proxy_manager')
        
        if service_type.lower() == "openai":
            api_key = kwargs.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key is required")
            model = kwargs.get('model', 'gpt-4o-mini')
            return OpenAISummarizer(api_key=api_key, model=model, proxy_manager=proxy_manager)
        
        elif service_type.lower() == "gemini":
            api_key = kwargs.get('api_key') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key is required")
            model = kwargs.get('model', 'gemini-1.5-flash')
            return GeminiSummarizer(api_key=api_key, model=model, proxy_manager=proxy_manager)
        
        elif service_type.lower() == "local":
            return LocalSummarizer()
        
        else:
            raise ValueError(f"Unsupported AI service: {service_type}")