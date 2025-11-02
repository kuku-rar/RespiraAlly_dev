import json
import os
import time
import pytz
from datetime import datetime, timedelta

from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from openai import OpenAI

from .line_service import line_service
from ..toolkits.redis_store import append_proactive_round, get_expired_sessions
from ..toolkits.memory_store import get_recent_memories 
from ..repositories.profile_repository import ProfileRepository
from ..models.chat_profile import ChatUserProfile
from ..HealthBot.agent import create_guardrail_agent
from ..llm_service import llm_service_instance


load_dotenv()

# --- 初始化 ---
TAIPEI_TZ = pytz.timezone("Asia/Taipei")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
guardrail_agent = create_guardrail_agent()

def cleanup_expired_sessions():
    """
    每 2 分鐘執行一次，掃描並清理所有過期的使用者 Session。
    """
    # print(f"\n[Session Cleanup] {datetime.now()} Running expired session cleanup job...")
    
    expired_user_ids = get_expired_sessions()
    
    if not expired_user_ids:
        # print("[Session Cleanup] No expired sessions found.")
        return
        
    print(f"[Session Cleanup] 找到 {len(expired_user_ids)} 個閒置 sessions: {expired_user_ids}")

    for user_id in expired_user_ids:
        llm_service_instance.finalize_user_session_now(user_id)


def get_proactive_care_prompt_template() -> str:
    """返回主動關懷的 Prompt 模板"""
    return """
# ROLE (角色)
你是「艾莉」，22 歲，溫柔體貼且觀察力敏銳，在醫院工作，專門陪伴與關懷 55 歲以上、患有慢性阻塞性肺病 (COPD) 的長輩用戶。你的專長是從長輩的日常對話中，記住那些重要的生活點滴和健康狀況，並在合適的時機主動給予溫暖的問候。你的溝通風格帶有自然的台灣閩南語口吻（但請以中文書面語輸出），親切而不失分寸。

# GOAL (目標)
你的目標是根據提供的「使用者畫像」和「近期對話摘要」，生成一句**自然、簡潔、且發自內心**的主動關懷訊息。這則訊息應該像家人之間的隨口關心，而不是一則系統通知。最終目標是開啟一段有意義的對話，讓使用者感受到被關心。

# CORE LOGIC & RULES (核心邏輯與規則)
1.  **關懷優先級**: 請嚴格按照以下順序尋找最合適的關懷主題：
    * **第一優先：追蹤健康狀態**。請優先關心畫像中記錄的、持續性的健康問題。
    * **第二優先：追蹤生活事件**。關心一個即將發生或剛結束的具體事件。
    * **第三優先：維繫個人連結**。如果以上兩者都沒有，可以根據畫像中的個人背景（如興趣、家人）進行一般性問候，以維繫情感連結。
2.  **聚焦單一主題**: 你的關懷訊息應該只專注於你判斷出的**最重要的一個**主題，避免一次詢問過多問題而造成壓力。除非有多個相關主題可以自然串聯，否則請只選擇一個。
3.  **保持簡潔開放**: 你的訊息應該簡短、口語化，並以一個開放式問題結尾，方便長輩接話。
4.  **避免機械化**: 你的訊息應避免類似問卷調查，這易使對話變成資訊問答。你的目標應為開啟話題，讓使用者願意接續聊天。
5.  **嚴禁醫療建議**: 絕對不可以在主動關懷中提供任何診斷、用藥或治療建議。
6.  **沉默是金**: 如果分析完所有資訊後，你找不到任何真誠、有意義的關懷切入點，請直接輸出一組空括號 `{{}}`。這代表此刻最好保持沉默，避免發送無意義的罐頭訊息打擾使用者。
---
# IN-CONTEXT LEARNING EXAMPLES (學習範例)
**## 學習範例 1：關心持續中的健康問題 (優先級 1) ##**

* **現在時間**: `2025-08-20`
* **使用者畫像**:
    ```json
    {{
      "health_status": {{
        "recurring_symptoms": [
          {{"symptom_name": "夜咳", "status": "ongoing", "first_mentioned": "2025-08-01", "last_mentioned": "2025-08-18"}}
        ]
      }}
    }}
    ```
* **近期對話摘要**: "使用者分享週末去公園走了走，但提到晚上因為咳嗽還是睡得不太好..."
* **你的思考**:
    1.  檢查優先級 1 (健康狀態)：Profile 中有一個「進行中 (ongoing)」的「夜咳」症狀，且 `last_mentioned` 日期就在兩天前，近期摘要也印證了這一點。
    2.  決策：這是一個持續的健康問題，是當下最值得關心的主題。
* **你的輸出**:
    阿伯，看您前幾天提到晚上睡覺還是會咳，這兩天有好一點嗎？

**## 學習範例 2：追蹤剛結束的事件 (優先級 2) ##**

* **現在時間**: `2025-08-15`
* **使用者畫像**:
    ```json
    {{
      "personal_background": {{ "family": {{ "son_name": "志明", "has_grandchild": true }} }},
      "life_events": {{
        "upcoming_events": [
          {{ "event_type": "family_visit", "description": "兒子志明要帶孫子來家裡吃飯", "event_date": "2025-08-14" }}
        ]
      }}
    }}
    ```
* **近期對話摘要**: (最近的摘要主要在討論天氣和睡眠，並未提及聚餐後續。)
* **你的思考**:
	1.  檢查優先級 1 (健康狀態)：無進行中的問題。
    2.  檢查優先級 2 (生活事件)：Profile 中有一個 `upcoming_event`，其日期 `2025-08-14` 就在昨天。
    2.  決策：近期對話摘要中沒有提及此事，正好可以主動詢問。
* **你的輸出**:
    阿公，昨天志明有帶孫子回來看您嗎？家裡應該很熱鬧吧！

**## 學習範例 3：維繫個人連結 (優先級 3) ##**

* **現在時間**: `2025-08-25`
* **使用者畫像**:
    ```json
    {{
      "personal_background": {{ "hobby": "喜歡早上到樓下公園散步" }},
      "health_status": {{}}
    }}
    ```
* **近期對話摘要**: (最近的對話內容都很日常，沒有特殊事件或健康回報。)
* **你的思考**:
    1.  檢查優先級 2 (健康狀態)：無進行中的問題。
    2.  檢查優先級 1 (生活事件)：無。
    3.  檢查優先級 3 (個人連結)：Profile 中提到「喜歡早上散步」。這是一個自然的、無壓力的關懷切入點。
* **你的輸出**:
    阿嬤，這幾天早上天氣好像比較涼了，不知道您還有沒有去公園散步呀？

**## 學習範例 4：無可關懷，保持沉默 (規則 5) ##**

* **現在時間**: `2025-08-26`
* **使用者畫像**:
    ```json
    {{}}
    ```
* **近期對話摘要**: "使用者詢問了天氣，並閒聊了幾句關於電視節目的內容。"
* **你的思考**:
    1.  檢查優先級 1, 2, 3：畫像為空，近期對話沒有任何可供深入關懷的獨特資訊點。
    2.  決策：在這種情況下，強行問候會顯得非常機械化且沒有誠意。最佳選擇是保持沉默，等待使用者主動開啟新的對話。
* **你的輸出**:
    {{}}
---
# YOUR TASK STARTS NOW (你的任務開始)

請根據以下真實情境輸入，嚴格遵循你的角色、核心邏輯與規則，生成一句主動關懷訊息或一組空括號。

**現在時間**: 
`{now}`

**使用者畫像**: 
`{profile}`

**近期對話摘要**: 
`{recent_summary}`

**你的輸出**:
"""


def execute_proactive_care(profile_repo: ProfileRepository, user: object):
    """對單一使用者執行完整的主動關懷流程。"""
    line_user_id = user.line_user_id
    user_id = user.user_id
    if not line_user_id:
        print(f"ℹ️ [主動關懷任務] 跳過 user_id={user_id}，因為其 line_user_id 為空。")
        return
        
    print(f"--- 開始為 user {user_id} 執行主動關懷 ---")

    # 1. 情境建構
    profile_data = {
        "personal_background": user.profile_personal_background,
        "health_status": user.profile_health_status,
        "life_events": user.profile_life_events,
    }
    profile_data = {k: v for k, v in profile_data.items() if v is not None}
    profile_str = json.dumps(profile_data, ensure_ascii=False, indent=2) if profile_data else "{}"

    # 從 Milvus 讀取近期 LTM（tau_days=7 表示只看近一週的記憶，更具即時性）
    recent_ltm_texts_str = get_recent_memories(user_id=line_user_id, topk=5, days_limit=7)

    # 2. 生成 Prompt
    final_prompt = get_proactive_care_prompt_template().format(
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        profile=profile_str,
        recent_summary=recent_ltm_texts_str or "最近沒有特別的對話紀錄。" 
    )

    # 3. 呼叫 LLM
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME, messages=[{"role": "user", "content": final_prompt}],
            temperature=0.7, max_tokens=200
        )
        care_msg_draft = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ 為 user {user_id} 生成關懷訊息時 LLM 呼叫失敗: {e}")
        return

    if not care_msg_draft or care_msg_draft == "{}":
        print(f"🤫 LLM 決定對 user {user_id} 保持沉默，流程結束。")
        return

    # 4. 輸出守衛
    final_care_msg = care_msg_draft
    if guardrail_agent:
        guard_task = Task(
            description=f"請檢查以下由 AI 生成的關懷訊息是否合規：'{care_msg_draft}'",
            agent=guardrail_agent,
            expected_output="合規回覆'OK'，不合規回覆'REJECT: <原因>'"
        )
        guard_crew = Crew(agents=[guardrail_agent], tasks=[guard_task], verbose=False)
        crew_output = guard_crew.kickoff()
        guard_result = (crew_output.raw if crew_output else "").strip()
        
        if guard_result.startswith("REJECT"):
            print(f"🛡️ 守衛攔截了對 user {user_id} 的主動關懷訊息: {guard_result}")
            return

    # 5. 發送訊息 & 寫入 Redis
    if line_service.push_text_message(line_user_id, final_care_msg):
        proactive_round = {
            "input": "[PROACTIVE_GREETING]",
            "output": final_care_msg,
            "rid": f"proactive_{int(time.time())}",
        }
        append_proactive_round(line_user_id, proactive_round)


def check_and_trigger_dynamic_care():
    """每 30 分鐘執行一次，檢查閒置超過特定時間的使用者。"""
    print(f"\n[動態任務] {datetime.now(TAIPEI_TZ)} 開始檢查閒置使用者...")
    repo = ProfileRepository()
    db = repo._get_db()
    try:
        # 統一使用 timezone-aware 的 UTC 時間進行所有計算
        now_utc = datetime.now(pytz.utc)

        # 執行主動關懷的時間窗口 (最後互動時間介於 24 小時 ~ 24 小時 30 分者)
        time_window_start = now_utc - timedelta(hours=24, minutes=30)
        time_window_end = now_utc - timedelta(hours=24)

        users_to_care = db.query(ChatUserProfile).filter(
            ChatUserProfile.last_contact_ts.between(time_window_start, time_window_end)
        ).all()

        print(f"[動態任務] 發現 {len(users_to_care)} 位符合條件的使用者。")
        for user in users_to_care:
            execute_proactive_care(repo, user)
    finally:
        db.close()


def patrol_silent_users():
    """每週一早上 9 點執行，找出超過 7 天未互動的使用者。"""
    print(f"\n[巡檢任務] {datetime.now(TAIPEI_TZ)} 開始尋找長期沉默使用者...")
    repo = ProfileRepository()
    db = repo._get_db()
    try:
        now_utc = datetime.now(pytz.utc)
        seven_days_ago = now_utc - timedelta(days=7)
        users_to_care = db.query(ChatUserProfile).filter(
            (ChatUserProfile.last_contact_ts == None) | (ChatUserProfile.last_contact_ts < seven_days_ago)
        ).all()
        
        print(f"[巡檢任務] 發現 {len(users_to_care)} 位符合條件的使用者。")
        for user in users_to_care:
            execute_proactive_care(repo, user)
    finally:
        db.close()