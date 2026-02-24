#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2026 tmwgsicp
# Licensed under the GNU Affero General Public License v3.0
# See LICENSE file in the project root for full license text.
# SPDX-License-Identifier: AGPL-3.0-only
"""
微信公众号文章API服务 - FastAPI版本
主应用文件
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

# 导入路由
from routes import article, articles, search, admin, login, image, health, stats

API_DESCRIPTION = """
微信公众号文章下载 API，支持文章解析、公众号搜索、文章列表获取等功能。

## 快速开始

1. 访问 `/login.html` 扫码登录微信公众号后台
2. 调用 `GET /api/public/searchbiz?query=公众号名称` 搜索目标公众号
3. 从返回结果中取 `fakeid`，调用 `GET /api/public/articles?fakeid=xxx` 获取文章列表
4. 对每篇文章调用 `POST /api/article` 获取完整内容

## 认证说明

所有核心接口都需要先登录。登录后凭证自动保存到 `.env` 文件，服务重启后无需重新登录（有效期约 4 天）。
"""

app = FastAPI(
    title="WeChat Download API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    license_info={
        "name": "AGPL-3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（注意：articles.router 必须在 search.router 之前注册，避免路由冲突）
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(stats.router, prefix="/api", tags=["统计信息"])
app.include_router(article.router, prefix="/api", tags=["文章内容"])
app.include_router(articles.router, prefix="/api/public", tags=["文章列表"])  # 必须先注册
app.include_router(search.router, prefix="/api/public", tags=["公众号搜索"])  # 后注册
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])
app.include_router(login.router, prefix="/api/login", tags=["登录"])
app.include_router(image.router, prefix="/api", tags=["图片代理"])

# 静态文件
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/api/redoc", include_in_schema=False)
async def redoc_html():
    """ReDoc 文档（使用 cdnjs 加速）"""
    return HTMLResponse("""<!DOCTYPE html>
<html><head>
<title>WeChat Download API - ReDoc</title>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
<style>body{margin:0;padding:0;}</style>
</head><body>
<redoc spec-url='/api/openapi.json'></redoc>
<script src="https://cdnjs.cloudflare.com/ajax/libs/redoc/2.1.5/bundles/redoc.standalone.min.js"></script>
</body></html>""")

# 静态页面路由
@app.get("/", include_in_schema=False)
async def root():
    """首页 - 重定向到管理页面"""
    return FileResponse(static_dir / "admin.html")

@app.get("/admin.html", include_in_schema=False)
async def admin_page():
    """管理页面"""
    return FileResponse(static_dir / "admin.html")

@app.get("/login.html", include_in_schema=False)
async def login_page():
    """登录页面"""
    return FileResponse(static_dir / "login.html")

@app.get("/verify.html", include_in_schema=False)
async def verify_page():
    """验证页面"""
    return FileResponse(static_dir / "verify.html")

# 启动事件
@app.on_event("startup")
async def startup_event():
    """启动时检查配置"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("\n" + "=" * 60)
        print("[WARNING] .env file not found")
        print("=" * 60)
        print("Please configure .env file or login via admin page")
        print("Visit: http://localhost:5000/admin.html")
        print("=" * 60 + "\n")
    else:
        print("\n" + "=" * 60)
        print("[OK] .env file loaded")
        print("=" * 60 + "\n")

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Wechat Article API Service - FastAPI Version")
    print("=" * 60)
    print("Admin Page: http://localhost:5000/admin.html")
    print("API Docs:   http://localhost:5000/api/docs")
    print("ReDoc Docs: http://localhost:5000/api/redoc")
    print("First time? Please login via admin page")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
