#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2026 tmwgsicp
# Licensed under the GNU Affero General Public License v3.0
# See LICENSE file in the project root for full license text.
# SPDX-License-Identifier: AGPL-3.0-only
"""
API限频模块
防止触发微信风控
"""

import time
from typing import Dict, Optional
from collections import deque
import threading

class RateLimiter:
    """
    智能限频器
    
    策略:
    1. 全局限制: 每分钟最多10个请求
    2. 单IP限制: 每分钟最多5个请求
    3. 文章获取: 每个文章间隔至少3秒
    """
    
    def __init__(self):
        self._global_requests = deque()  # 全局请求记录
        self._ip_requests: Dict[str, deque] = {}  # IP请求记录
        self._article_requests = deque()  # 文章请求记录
        self._lock = threading.Lock()
        
        # 限制配置
        self.GLOBAL_WINDOW = 60  # 全局窗口60秒
        self.GLOBAL_LIMIT = 10  # 全局限制10个请求/分钟
        
        self.IP_WINDOW = 60  # IP窗口60秒
        self.IP_LIMIT = 5  # 单IP限制5个请求/分钟
        
        self.ARTICLE_INTERVAL = 3  # 文章获取间隔3秒
    
    def check_rate_limit(self, ip: str, endpoint: str) -> tuple[bool, Optional[str]]:
        """
        检查是否超过限频
        
        Args:
            ip: 客户端IP
            endpoint: 请求端点
            
        Returns:
            (是否允许, 错误消息)
        """
        with self._lock:
            current_time = time.time()
            
            # 清理过期记录
            self._cleanup_old_requests(current_time)
            
            # 检查全局限制
            if len(self._global_requests) >= self.GLOBAL_LIMIT:
                oldest = self._global_requests[0]
                wait_time = int(self.GLOBAL_WINDOW - (current_time - oldest) + 1)
                return False, f"全局请求过多，请{wait_time}秒后重试"
            
            # 检查IP限制
            if ip not in self._ip_requests:
                self._ip_requests[ip] = deque()
            
            if len(self._ip_requests[ip]) >= self.IP_LIMIT:
                oldest = self._ip_requests[ip][0]
                wait_time = int(self.IP_WINDOW - (current_time - oldest) + 1)
                return False, f"请求过于频繁，请{wait_time}秒后重试"
            
            # 检查文章获取间隔
            if endpoint == "/api/article" and self._article_requests:
                last_article = self._article_requests[-1]
                if current_time - last_article < self.ARTICLE_INTERVAL:
                    wait_time = int(self.ARTICLE_INTERVAL - (current_time - last_article) + 1)
                    return False, f"文章获取过快，请{wait_time}秒后重试（防风控）"
            
            # 记录请求
            self._global_requests.append(current_time)
            self._ip_requests[ip].append(current_time)
            
            if endpoint == "/api/article":
                self._article_requests.append(current_time)
            
            return True, None
    
    def _cleanup_old_requests(self, current_time: float):
        """清理过期的请求记录"""
        # 清理全局请求
        while self._global_requests and current_time - self._global_requests[0] > self.GLOBAL_WINDOW:
            self._global_requests.popleft()
        
        # 清理IP请求
        for ip in list(self._ip_requests.keys()):
            while self._ip_requests[ip] and current_time - self._ip_requests[ip][0] > self.IP_WINDOW:
                self._ip_requests[ip].popleft()
            
            # 删除空记录
            if not self._ip_requests[ip]:
                del self._ip_requests[ip]
        
        # 清理文章请求（保留最近10条）
        while len(self._article_requests) > 10:
            self._article_requests.popleft()
    
    def get_stats(self) -> Dict:
        """获取限频统计"""
        with self._lock:
            current_time = time.time()
            self._cleanup_old_requests(current_time)
            
            return {
                "global_requests": len(self._global_requests),
                "global_limit": self.GLOBAL_LIMIT,
                "active_ips": len(self._ip_requests),
                "article_requests": len(self._article_requests)
            }

# 全局限频器实例
rate_limiter = RateLimiter()

