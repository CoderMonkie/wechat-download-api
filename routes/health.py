#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2026 tmwgsicp
# Licensed under the GNU Affero General Public License v3.0
# See LICENSE file in the project root for full license text.
# SPDX-License-Identifier: AGPL-3.0-only
"""
健康检查路由
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    framework: str

@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """
    检查服务健康状态
    
    Returns:
        服务状态信息
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "framework": "FastAPI"
    }

