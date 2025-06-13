#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 服務器管理腳本
================

用於管理工作分配系統的API服務器，支援：
- start: 啟動服務器
- stop: 停止服務器  
- restart: 重啟服務器
- status: 檢查服務器狀態
"""

import os
import sys
import time
import subprocess
import argparse

# API服務器配置
API_SERVER_SCRIPT = "server/api_server.py"
API_PORT = 7777
PYTHON_PATH = "./.venv/bin/python"

def run_command(cmd, capture_output=True):
    """執行系統命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def stop_server():
    """停止API服務器"""
    print("🛑 正在停止API服務器...")
    
    # 使用pkill停止所有api_server進程
    success, stdout, stderr = run_command("pkill -f api_server")
    
    # pkill返回0表示找到並終止了進程，返回1表示沒找到進程
    if success or "No matching processes" in stderr:
        print("✅ API服務器已停止")
    else:
        print("ℹ️  沒有找到運行中的API服務器")
    
    # 等待一下確保進程完全停止
    time.sleep(2)
    return True

def check_port():
    """檢查端口是否被占用"""
    success, stdout, stderr = run_command(f"lsof -i :{API_PORT}")
    return success, stdout

def start_server():
    """啟動API服務器"""
    print("🚀 正在啟動API服務器...")
    
    # 檢查端口是否可用
    port_in_use, port_info = check_port()
    if port_in_use:
        print(f"❌ 端口 {API_PORT} 已被佔用:")
        print(port_info)
        print("   請先執行 'python manage_server.py stop' 停止現有服務器")
        return False
    
    # 檢查Python環境和腳本文件
    if not os.path.exists(PYTHON_PATH):
        print(f"❌ 找不到Python環境: {PYTHON_PATH}")
        return False
    
    if not os.path.exists(API_SERVER_SCRIPT):
        print(f"❌ 找不到API服務器腳本: {API_SERVER_SCRIPT}")
        return False
    
    # 啟動服務器
    try:
        cmd = f"{PYTHON_PATH} {API_SERVER_SCRIPT}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid  # 創建新的進程組
        )
        
        # 等待一下確認服務器啟動
        time.sleep(4)
        
        # 檢查端口是否開始監聽
        port_in_use, port_info = check_port()
        if port_in_use:
            print(f"✅ API服務器已啟動")
            print(f"🌐 服務地址: http://localhost:{API_PORT}")
            # 顯示端口信息
            if port_info.strip():
                lines = port_info.strip().split('\n')
                if len(lines) > 1:  # 跳過標題行
                    for line in lines[1:]:
                        if 'LISTEN' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                print(f"📡 PID: {parts[1]}")
                            break
            return True
        else:
            print("❌ 服務器啟動失敗，端口未監聽")
            return False
            
    except Exception as e:
        print(f"❌ 啟動服務器時發生錯誤: {e}")
        return False

def restart_server():
    """重啟API服務器"""
    print("🔄 正在重啟API服務器...")
    stop_server()
    time.sleep(1)
    return start_server()

def check_status():
    """檢查服務器狀態"""
    print("📊 API服務器狀態檢查")
    print("=" * 40)
    
    # 檢查進程
    success, stdout, stderr = run_command("pgrep -f api_server")
    if success and stdout.strip():
        pids = stdout.strip().split('\n')
        print("🟢 API服務器進程:")
        for pid in pids:
            if pid:
                print(f"   PID: {pid}")
    else:
        print("🔴 沒有找到API服務器進程")
    
    # 檢查端口
    port_in_use, port_info = check_port()
    if port_in_use:
        print(f"🟢 端口 {API_PORT} 正在使用:")
        if port_info.strip():
            lines = port_info.strip().split('\n')
            for line in lines[1:]:  # 跳過標題行
                if 'LISTEN' in line:
                    print(f"   {line}")
    else:
        print(f"🔴 端口 {API_PORT} 未被使用")
    
    # 嘗試連接測試
    try:
        import urllib.request
        import urllib.error
        
        req = urllib.request.Request(f"http://localhost:{API_PORT}/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                print("🟢 API服務器響應正常")
            else:
                print(f"🟡 API服務器響應異常 (狀態碼: {response.getcode()})")
    except urllib.error.URLError as e:
        print(f"🔴 API服務器連接失敗: {e}")
    except Exception as e:
        print(f"🔴 連接測試發生錯誤: {e}")

def main():
    parser = argparse.ArgumentParser(description="API服務器管理工具")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"],
                      help="操作類型")
    
    args = parser.parse_args()
    
    if args.action == "start":
        success = start_server()
    elif args.action == "stop":
        success = stop_server()
    elif args.action == "restart":
        success = restart_server()
    elif args.action == "status":
        check_status()
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 