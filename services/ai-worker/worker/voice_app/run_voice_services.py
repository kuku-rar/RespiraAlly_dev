#!/usr/bin/env python3
"""
AI Worker Voice Services Launcher
啟動語音相關服務的腳本
"""

import os
import sys
import logging
import argparse
import subprocess
import threading
import time

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_voice_worker():
    """運行語音工作者（RabbitMQ消費者）"""
    try:
        logger.info("正在啟動Voice Worker...")
        from voice_worker import main as worker_main
        worker_main()
    except Exception as e:
        logger.error("Voice Worker啟動失敗: %s", e)

def run_flask_api():
    """運行Flask API服務"""
    try:
        logger.info("正在啟動Voice Flask API...")
        
        # 設置環境變量
        os.environ.setdefault("VOICE_FLASK_HOST", "0.0.0.0")
        os.environ.setdefault("VOICE_FLASK_PORT", "8001")
        os.environ.setdefault("FLASK_DEBUG", "False")
        
        # 使用Gunicorn運行Flask應用
        cmd = [
            "gunicorn",
            "--bind", f"{os.environ['VOICE_FLASK_HOST']}:{os.environ['VOICE_FLASK_PORT']}",
            "--workers", "2",
            "--worker-class", "sync",
            "--timeout", "300",
            "--max-requests", "1000",
            "--max-requests-jitter", "100",
            "--preload",
            "voice_flask_app:app"
        ]
        
        logger.info("執行命令: %s", " ".join(cmd))
        subprocess.run(cmd, check=True)
        
    except FileNotFoundError:
        logger.warning("Gunicorn未找到，使用Flask開發服務器...")
        try:
            from voice_flask_app import app
            host = os.getenv("VOICE_FLASK_HOST", "0.0.0.0")
            port = int(os.getenv("VOICE_FLASK_PORT", "8001"))
            app.run(host=host, port=port, debug=False, threaded=True)
        except Exception as e:
            logger.error("Flask API啟動失敗: %s", e)
    except Exception as e:
        logger.error("Voice Flask API啟動失敗: %s", e)

def run_both_services():
    """同時運行Worker和Flask API"""
    logger.info("同時啟動Voice Worker和Flask API...")
    
    # 啟動Worker線程
    worker_thread = threading.Thread(target=run_voice_worker, daemon=True)
    worker_thread.start()
    
    # 給Worker一些時間啟動
    time.sleep(2)
    
    # 啟動Flask API（主線程）
    run_flask_api()

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="AI Worker Voice Services Launcher")
    parser.add_argument(
        "--service",
        choices=["worker", "api", "both"],
        default="both",
        help="選擇要啟動的服務: worker(RabbitMQ消費者), api(Flask API), both(兩者)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Flask API主機地址 (默認: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Flask API端口 (默認: 8001)"
    )
    
    args = parser.parse_args()
    
    # 設置環境變量
    os.environ["VOICE_FLASK_HOST"] = args.host
    os.environ["VOICE_FLASK_PORT"] = str(args.port)
    
    logger.info("啟動AI Worker Voice Services...")
    logger.info("服務類型: %s", args.service)
    
    try:
        if args.service == "worker":
            run_voice_worker()
        elif args.service == "api":
            run_flask_api()
        elif args.service == "both":
            run_both_services()
            
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在停止服務...")
    except Exception as e:
        logger.error("服務啟動失敗: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()