"""
AI Summarizer for WeChat chat logs
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging
import os
from openai import OpenAI
import google.generativeai as genai



class BaseSummarizer(ABC):
    """AI总结器基类"""
    
    @abstractmethod
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """总结聊天记录"""
        pass


class OpenAISummarizer(BaseSummarizer):
    """OpenAI总结器"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """使用OpenAI总结聊天记录"""
        if not chat_logs:
            return f"群聊 '{group_name}' 暂无聊天记录"
        
        # 格式化聊天记录
        formatted_messages = self._format_messages(chat_logs)
        
        # 构建提示词
        prompt = self._build_prompt(group_name, formatted_messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的聊天记录分析师，善于从群聊记录中提取关键信息并生成简洁有用的总结。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
    
    def _format_messages(self, chat_logs: List[Dict]) -> str:
        """格式化聊天消息"""
        messages = []
        for log in chat_logs:
            time_str = log.get('time', '')
            sender = log.get('senderName', '未知用户')
            content = log.get('content', '')
            
            # 跳过空消息或系统消息
            if not content or log.get('type') != 1:
                continue
                
            messages.append(f"[{time_str}] {sender}: {content}")
        
        return "\n".join(messages[-50:])  # 只取最近50条消息避免token超限
    
    def _build_prompt(self, group_name: str, formatted_messages: str) -> str:
        """构建AI提示词"""
        return f"""
请分析群聊 '{group_name}' 的聊天记录，重点关注核心话题、有价值的观点和重要信息分享。忽略没有意义的图片链接、表情符号等内容。

聊天记录：
{formatted_messages}

请按以下格式输出结构化总结：

## 📊 群聊概况
- **群聊名称**: {group_name}
- **活跃成员**: [统计发言人数]
- **消息总数**: [统计有效消息数量]
- **时间跨度**: [记录时间范围]

## 🔥 核心话题
[按重要性排序，列出最多 20 个主要讨论话题，每个话题包含关键观点]

1. **话题一**: 
   - 核心内容: 
   - 主要观点: 
   - 参与讨论: 

2. **话题二**: 
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
[整理群内讨论的问题和解答，最多 20 个问题]

**Q1**: [问题描述]
**A1**: [解答内容]

**Q2**: [问题描述] 
**A2**: [解答内容]

## 🎯 待跟进事项
[需要后续关注或行动的事项]

- [ ] [待办事项1]
- [ ] [待办事项2]

## 📝 备注
[其他值得关注的信息或观察]

---
*本总结基于AI分析生成，如有遗漏请参考原始聊天记录 by jovix*
"""


class LocalSummarizer(BaseSummarizer):
    """本地总结器（简单文本处理）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
        return summary


class GeminiSummarizer(BaseSummarizer):
    """Google Gemini总结器"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        self.logger = logging.getLogger(__name__)
    
    def summarize_chat_logs(self, chat_logs: List[Dict], group_name: str) -> str:
        """使用Google Gemini总结聊天记录"""
        if not chat_logs:
            return f"群聊 '{group_name}' 暂无聊天记录"
        
        # 格式化聊天记录
        formatted_messages = self._format_messages(chat_logs)
        
        # 构建提示词
        prompt = self._build_prompt(group_name, formatted_messages)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            self.logger.exception(e)
            raise RuntimeError(f"Gemini API调用失败: {str(e)}")
    
    def _format_messages(self, chat_logs: List[Dict]) -> str:
        """格式化聊天消息"""
        messages = []
        for log in chat_logs:
            time_str = log.get('time', '')
            sender = log.get('senderName', '未知用户')
            content = log.get('content', '')
            
            # 跳过空消息或系统消息
            if not content or log.get('type') != 1:
                continue
                
            messages.append(f"[{time_str}] {sender}: {content}")
        
        return "\n".join(messages[-50:])  # 只取最近50条消息避免token超限
    
    def _build_prompt(self, group_name: str, formatted_messages: str) -> str:
        """构建AI提示词"""
        return f"""
请分析群聊 '{group_name}' 的聊天记录，重点关注核心话题、有价值的观点和重要信息分享。忽略没有意义的图片链接、表情符号等内容。

聊天记录：
{formatted_messages}

请按以下格式输出结构化总结：

## 📊 群聊概况
- **群聊名称**: {group_name}
- **活跃成员**: [统计发言人数]
- **消息总数**: [统计有效消息数量]
- **时间跨度**: [记录时间范围]

## 🔥 核心话题
[按重要性排序，列出3-5个主要讨论话题，每个话题包含关键观点]

1. **话题一**: 
   - 核心内容: 
   - 主要观点: 
   - 参与讨论: 

2. **话题二**: 
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
[尽可能多的整理群内讨论的有价值的问题和解答]

**Q1**: [问题描述]
**A1**: [解答内容]

**Q2**: [问题描述] 
**A2**: [解答内容]

## 🎯 待跟进事项
[需要后续关注或行动的事项]

- [ ] [待办事项1]
- [ ] [待办事项2]

## 📝 备注
[其他值得关注的信息或观察]

---
*本总结基于AI分析生成，如有遗漏请参考原始聊天记录*
"""


class SummarizerFactory:
    """总结器工厂类"""
    
    @staticmethod
    def create_summarizer(service_type: str, **kwargs) -> BaseSummarizer:
        """创建总结器实例"""
        if service_type.lower() == "openai":
            api_key = kwargs.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key is required")
            model = kwargs.get('model', 'gpt-4o-mini')
            return OpenAISummarizer(api_key=api_key, model=model)
        
        elif service_type.lower() == "gemini":
            api_key = kwargs.get('api_key') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key is required")
            model = kwargs.get('model', 'gemini-1.5-flash')
            return GeminiSummarizer(api_key=api_key, model=model)
        
        elif service_type.lower() == "local":
            return LocalSummarizer()
        
        else:
            raise ValueError(f"Unsupported AI service: {service_type}")