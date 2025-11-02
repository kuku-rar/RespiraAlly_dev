import importlib
import os
import sys
from typing import Any, Dict

# 禁用 CrewAI 遙測功能（避免連接錯誤）
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# 兼容「模組方式」與「直接腳本」兩種執行情境
try:
    from .chat_pipeline import AgentManager, handle_user_message
    from .HealthBot.agent import finalize_session
except Exception:
    # 若以腳本模式執行（無封包上下文），把 /app/worker 加進 sys.path
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from llm_app.chat_pipeline import AgentManager, handle_user_message
    from llm_app.HealthBot.agent import finalize_session


class LLMService:
    """LLM 微服務接口，負責 Milvus 連接和多用戶會話管理"""

    def __init__(self) -> None:
        print("🚀 Initializing a new LLMService instance...")
        self.agent_manager = AgentManager()
        self._milvus_connected = False
        self._ensure_milvus_connection()

    def _ensure_milvus_connection(self):
        """確保 Milvus 連接（長期記憶功能需要）"""
        if self._milvus_connected:
            return

        try:
            from pymilvus import connections

            milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
            connections.connect(alias="default", uri=milvus_uri)
            self._milvus_connected = True
            print("✅ Milvus 連接成功")
        except Exception as e:
            print(f"⚠️  Milvus 連接失敗: {e}")
            print("長期記憶功能可能不可用")


    def generate_response(self, task_data: Dict[str, Any]) -> str:
        """生成回應（包含完整長期追蹤功能和獨立用戶會話管理）

        期待的 task_data 欄位對應：
        - patient_id -> 對應 Final 的 user_id
        - text -> 對應 Final 的 query（可選）
        - object_name -> 對應 Final 的 audio_id（可選）
        - line_user_id -> 對應 LINE 的使用者 ID
        """
        if not isinstance(task_data, dict):
            return "參數格式錯誤"

        user_id = str(
            task_data.get("patient_id") or task_data.get("user_id") or "unknown_user"
        )
        line_user_id = task_data.get("line_user_id")
        query = str(task_data.get("text") or "").strip()
        audio_id = None
        # 優先使用 object_name 當 audio_id；若沒有且為純文字則由流程自動以 hash 產生
        if task_data.get("object_name"):
            audio_id = str(task_data.get("object_name"))

        if not query and not audio_id:
            return "缺少必要輸入（text 或 object_name 至少一項）"

        if not line_user_id:
            print(f"⚠️ 警告：來自 user_id {user_id} 的請求缺少 line_user_id，Profile 功能將受限。")


        try:
            # 確保 Milvus 連接（長期記憶功能）
            self._ensure_milvus_connection()

            # Session 的刷新改以 handle_user_message -> log_session -> append_round 完成
            response_text = handle_user_message(
                agent_manager=self.agent_manager,
                user_id=user_id,
                line_user_id=line_user_id,
                query=query,
                audio_id=audio_id,
                is_final=True,
            )
            return response_text
        except Exception as e:
            print(f"[LLMService] 發生錯誤：{e}")
            return "抱歉，無法生成回應。"

    def finalize_user_session_now(self, user_id: str):
        """
        供排程任務呼叫，立即執行指定用戶的 Session 結束流程。
        """
        print(f"⏳ 執行閒置對話的收尾流程：user_id = {user_id}")
        try:
            # 整理長期記憶並釋放 Agent
            finalize_session(user_id)
            self.agent_manager.release_health_agent(user_id)
            print(f"✅ 對話收尾完成：user {user_id}")
        except Exception as e:
            print(f"⚠️ 對話收尾出錯：user {user_id}: {e}")
            # 即使失敗，也確保 agent 被釋放
            self.agent_manager.release_health_agent(user_id)

llm_service_instance = LLMService()

def run_interactive_test():
    """互動式測試 - 固定用戶 test_user1，測試 5 分鐘釋放功能"""
    print("🏥 Beloved Grandson LLM Service - 互動測試模式")
    print("=" * 60)
    print("💡 功能說明：")
    print("  - 固定用戶：test_user1")
    print("  - 有輸入時重新開始計算 5 分鐘")
    print("  - 5 分鐘無活動後自動釋放 Agent")
    print("  - 使用 Ctrl+C 退出")
    print("=" * 60)

    # 初始化服務
    llm_service = LLMService()
    user_id = "test_user1"

    print("\n📋 使用說明：")
    print("  - 直接輸入您的訊息")
    print("  - 按 Ctrl+C 退出測試")
    print("=" * 60)

    while True:
        try:
            message = input("\n請輸入您的訊息: ").strip()

            if not message:
                continue

            # 構建 task_data
            task_data = {"patient_id": user_id, "text": message}

            print(f"\n🗣️  輸入：{message}")
            response = llm_service_instance.generate_response(task_data)
            print(f"🤖 AI 回應：{response}")

        except KeyboardInterrupt:
            print("\n\n🔚 收到 Ctrl+C 中斷信號，正在清理...")
            print("👋 再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")


if __name__ == "__main__":
    # 載入環境變數
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    # 建議以模組模式執行，確保封包路徑正確：
    #   python -m llm_app.llm_service
    run_interactive_test()
    # 測試 LLMService
    # 0. .env.example 改成 .env ，可以不做任何設定
    # 1. 啟動ai-worker和相關的容器
    # docker-compose -f docker-compose.dev.yml up -d --build ai-worker

    # 2. 執行測試腳本
    # docker-compose -f docker-compose.dev.yml exec ai-worker python worker/llm_app/llm_service.py

    #! task_data： LLM RAG 需要什麼內容，請找做後端的人要，後端會處理並將資料放置在task_data裡面
