#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
啟動API Server腳本
==================

便於啟動工作分配管理系統API服務
"""

import os
import sys
import subprocess

def start_server():
    """啟動API Server"""
    # 取得當前腳本目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # API server檔案路徑
    api_server_path = os.path.join(current_dir, 'api_server.py')
    
    print("🚀 啟動工作分配管理系統 API Server...")
    print(f"📁 服務位置: {api_server_path}")
    print("🌐 服務位址: http://localhost:7777")
    print("⏹️  按 Ctrl+C 停止服務")
    print("-" * 50)
    
    try:
        # 取得專案根目錄路徑
        project_root = os.path.dirname(current_dir)
        
        # 使用專案的.venv虛擬環境
        python_path = os.path.join(project_root, ".venv", "bin", "python")
        
        # 檢查虛擬環境是否存在
        if not os.path.exists(python_path):
            print(f"❌ 找不到虛擬環境: {python_path}")
            print("請先建立並安裝虛擬環境:")
            print("python3 -m venv .venv")
            print("source .venv/bin/activate")
            print("pip install -r server/requirements_api.txt")
            return
        
        print(f"🐍 使用Python: {python_path}")
        
        # 啟動server
        subprocess.run([python_path, api_server_path], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API Server已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {str(e)}")

if __name__ == "__main__":
    start_server() 