"""
WeChat API Client for chatlog service
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging


class WeChatAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5030", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def get_chat_rooms(self, keyword: str = "", limit: int = 100) -> List[Dict]:
        """获取群聊列表"""
        url = f"{self.base_url}/api/v1/chatroom"
        params = {
            "format": "json",
            "limit": str(limit),
            "offset": "0",
            "keyword": keyword
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            self.logger.error(f"Error fetching chat rooms: {e}")
            return []
    
    def get_chat_logs(self, talker: str, time_range: str = None, 
                     limit: int = 200, offset: int = 0) -> List[Dict]:
        """
        获取指定群聊的聊天记录
        
        Args:
            talker: 群聊ID或群名
            time_range: 时间范围，格式如 "2023-01-01" 或 "2023-01-01~2023-01-02"
            limit: 返回记录数量
            offset: 分页偏移量
        """
        url = f"{self.base_url}/api/v1/chatlog"
        params = {
            "format": "json",
            "talker": talker,
            "limit": str(limit),
            "offset": str(offset)
        }
        
        if time_range:
            params["time"] = time_range
            
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching chat logs for {talker}: {e}")
            return []
    
    def get_yesterday_chats(self, talker: str, limit: int = 200) -> List[Dict]:
        """获取昨天的聊天记录"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self.get_chat_logs(talker, time_range=yesterday, limit=limit)
    
    def get_chat_logs_by_date_range(self, talker: str, start_date: str, 
                                   end_date: str, limit: int = 200) -> List[Dict]:
        """获取指定日期范围的聊天记录"""
        time_range = f"{start_date}~{end_date}"
        return self.get_chat_logs(talker, time_range=time_range, limit=limit)
    
    def find_group_by_name(self, group_name: str) -> Optional[Dict]:
        """根据群名查找群聊信息"""
        chat_rooms = self.get_chat_rooms(keyword=group_name)
        for room in chat_rooms:
            if room.get("nickName") == group_name or room.get("name") == group_name:
                return room
        return None
    
    def health_check(self) -> bool:
        """检查API服务是否可用"""
        try:
            url = f"{self.base_url}/api/v1/session"
            params = {"format": "json", "limit": "1", "offset": "0"}
            response = self.session.get(url, params=params, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False