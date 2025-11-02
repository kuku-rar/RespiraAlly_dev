#!/usr/bin/env python3
"""
測試診斷端點腳本
用於檢查 API 的各個層級是否正常工作
"""
import requests
import json
import os

# 從環境變數獲取 API Base URL，或使用預設值
API_BASE = os.getenv('API_BASE_URL', 'https://8477c7faaaed.ngrok-free.app/api/v1')

def test_endpoint(url, headers=None, description=""):
    """測試單一端點"""
    print(f"\n🧪 測試: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 成功")
            data = response.json()
            print(f"回應: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 失敗")
            print(f"錯誤: {response.text}")
            
    except Exception as e:
        print(f"❌ 連接錯誤: {e}")

def main():
    print("🔍 API 診斷測試開始")
    print(f"Base URL: {API_BASE}")
    
    # 1. 基本健康檢查（無需認證）
    test_endpoint(
        f"{API_BASE}/debug/health",
        description="基本健康檢查 (無需認證)"
    )
    
    # 2. 資料庫連接測試（無需認證）
    test_endpoint(
        f"{API_BASE}/debug/db-test",
        description="資料庫連接測試 (無需認證)"
    )
    
    # 3. 取得登入 token（如果有現有的認證端點）
    print(f"\n📝 請提供 JWT token 以測試認證相關端點")
    print(f"你可以通過以下方式獲取：")
    print(f"1. 瀏覽器開發者工具中查看 localStorage['access_token']")
    print(f"2. 或手動登入後複製 token")
    
    token = input("請輸入 JWT token (或按 Enter 跳過認證測試): ").strip()
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. JWT 認證測試
        test_endpoint(
            f"{API_BASE}/debug/auth-test",
            headers=headers,
            description="JWT 認證測試"
        )
        
        # 5. 簡化總覽查詢測試
        test_endpoint(
            f"{API_BASE}/debug/overview-simple",
            headers=headers,
            description="簡化總覽查詢測試"
        )
        
        # 6. 測試原始的問題端點
        print(f"\n🎯 測試原始問題端點:")
        
        test_endpoint(
            f"{API_BASE}/overview/kpis",
            headers=headers,
            description="原始 KPIs 端點"
        )
        
        test_endpoint(
            f"{API_BASE}/overview/trends",
            headers=headers,
            description="原始 Trends 端點"
        )
        
        test_endpoint(
            f"{API_BASE}/overview/adherence",
            headers=headers,
            description="原始 Adherence 端點"
        )
    
    print(f"\n✨ 診斷測試完成")

if __name__ == "__main__":
    main()