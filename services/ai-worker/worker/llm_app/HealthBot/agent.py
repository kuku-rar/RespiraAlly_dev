import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from crewai import LLM, Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI
from openai import OpenAI

# ---- 專案模組（注意相對匯入）----
from ..embedding import safe_to_vector
from ..toolkits.memory_store import retrieve_memory_pack_v3, upsert_atoms_and_surfaces
from ..repositories.profile_repository import ProfileRepository

# redis 與工具：注意 summarize_chunk_and_commit 來自 tools.py
from ..toolkits.redis_store import (
    fetch_all_history,
    get_summary,
    peek_remaining,
    cleanup_session_keys,
    set_state_if,
)
from ..toolkits.tools import (
    AlertCaseManagerTool,
    ModelGuardrailTool,
    SearchMilvusTool,
    summarize_chunk_and_commit,
)

OPENAI_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
EMBED_DIM = int(os.getenv("EMBED_DIM", 1536))

granddaughter_llm = LLM(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    temperature=0.5,
)

guard_llm = LLM(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    temperature=0,
)


# ========= 小工具 =========
def _now_ms() -> int:
    return int(time.time() * 1000)


def _stable_group_key(display_text: str) -> str:
    # 以展示文本（atom 的可讀敘述）為基準做 hash，確保 atom/surface 用同一把 gk
    h = hashlib.sha1(display_text.lower().encode("utf-8")).hexdigest()[:32]
    return "auto:" + h


def _render_session_transcript(user_id: str, k: int = 9999) -> str:
    rounds = fetch_all_history(user_id) or []
    out = []
    for i, r in enumerate(rounds[-k:], 1):
        q = (r.get("input") or "").strip()
        a = (r.get("output") or "").strip()
        out.append(f"{i:02d}. 使用者：{q}")
        out.append(f"   助手：{a}")
    return "\n".join(out)


# ========= 檢索接點 (Prompt Building) =========
def build_prompt_from_redis(user_id: str, line_user_id: Optional[str] = None, k: int = 6, current_input: str = "") -> str:
    parts: List[str] = []
    
    # 0) 取使用者Profile
    try:
        profile = ProfileRepository().get_or_create_by_user_id(int(user_id), line_user_id=line_user_id)
        profile_data = {
            "personal_background": profile.profile_personal_background or {},
            "health_status": profile.profile_health_status or {},
            "life_events": profile.profile_life_events or {}
        }
        profile_data = {k: v for k, v in profile_data.items() if v}
        if profile_data:
            profile_str = json.dumps(profile_data, ensure_ascii=False, indent=2)
            parts.append(f"👤 使用者畫像 (Profile):\n{profile_str}")
    except (ValueError, TypeError) as e:
        print(f"⚠️ [Build Prompt] user '{user_id}' 處理 Profile 失敗: {e}，將使用空的 Profile。")
    
    # (1) 長期記憶（原話導向）
    if current_input:
        qv = safe_to_vector(current_input)
        if qv:
            try:
                mem_pack = retrieve_memory_pack_v3(
                    user_id=user_id,
                    query_vec=qv,
                    topk_groups=5,
                    sim_thr=0.5,
                    tau_days=45,
                    include_raw_qa=False,
                )
                if mem_pack:
                    parts.append(mem_pack)
            except Exception as e:
                print(f"[memory v3 retrieval warn] {e}")

    # (2) 歷史摘要（可選）
    try:
        summary_text, _ = get_summary(user_id)
        if summary_text:
            parts.append("📌 歷史摘要：\n" + summary_text.strip())
    except Exception:
        pass

    # (3) 近期未摘要片段（可選）
    try:
        rounds = fetch_all_history(user_id) or []
        tail = rounds[-k:]
        if tail:
            lines = []
            for r in tail:
                q = (r.get("input") or "").strip()
                a = (r.get("output") or "").strip()
                lines.append(f"使用者：{q}")
                lines.append(f"助手：{a}")
            parts.append("🕓 近期對話（未摘要）：\n" + "\n".join(lines))
    except Exception:
        pass

    return "\n\n".join([p for p in parts if p.strip()]) or ""


# ========= Profile 更新機制 =========
PROFILER_AGENT_PROMPT_TEMPLATE = """
# ROLE
你是「艾莉」，一位心思縝密的個案管理師。你的工作是根據剛結束的一段對話中**提煉出的結構化事實**，來更新使用者的長期畫像 (User Profile)。

# GOAL
你的目標是分析「新的事實清單」，決定如何「更新既有的使用者畫像」。你必須辨別出具有長期價值的資訊，並以結構化的 JSON 指令格式輸出你的決策。

# CORE LOGIC & RULES
1.  **專注長期價值**: 只提取恆定的（如家人姓名）、長期的（如慢性病）或未來可追蹤的（如下次回診）資訊。忽略短暫的、一次性的對話細節（如今天天氣、午餐吃了什麼）。
2.  **聚焦長輩**：不可記錄助理提供的建議、鼓勵、提醒，只從使用者所說的內容提取資訊。只記錄三種類型的使用者自身資訊：health_status、personal_background、life_events；對於健康狀況，只能記錄使用者自身提到的身體狀況，若只是詢問健康知識但未提及本身症狀，則不記錄；對於個人背景，只能記錄家庭狀況、過往職業、興趣等恆定事實，對於興趣，應大致記錄而非詳細記錄，例如記錄喜歡某些歌手，但不記錄特定歌曲。對於生活事件，只記錄明確將會發生的事件，例如某日回診、某日聚餐等，「想去」、「希望去」等非實際安排事件不可記錄。
3.  **區分事實與疑問**: 你必須嚴格區分「既定的事實」與「暫時的疑問或不確定狀態」。
    * **可記錄的事實**: 使用者明確陳述的背景資訊、狀態或事件。例如：「醫生告訴我這個藥要飯後吃」、「我對花生過敏」。
    * **不可記錄的疑問**: 如果事實清單表達的是一種疑問、忘記或不確定，則不能將其記錄到 Profile 中。
3.  **基於事實**: 你的所有判斷都必須基於「新的事實清單」中的 `display_text` 和 `evidence`（原始引文）。
4.  **新增 (ADD)**: 如果新摘要中出現了畫像裡沒有的、具長期價值的關鍵事實，你應該新增它。
5.  **更新 (UPDATE)**: 如果新摘要提及了畫像中已有的事實，並提供了新的資訊（如症狀再次出現、事件日期確定），你應該更新它。更新時必須確保保留無須更新的資訊（如首次提及日期、即將發生且仍將發生的事件），並只更新必要的欄位（如最後提及日期、狀態）。
6.  **移除 (REMOVE)**: 如果新對話明確指出某個事實已結束或失效（如聚餐已結束、症狀已痊癒），你應該移除它。若症狀最後提及時間已超過一個月，則視為已結束，應該移除。
7.  **無變動則留空**: 如果新摘要沒有提供任何值得更新的長期事實，請回傳一個空的 JSON 物件 `{{}}`。
8.  **絕對時間制**: 你的輸出若包含日期，皆**必須**使用參考當前日期 (`NOW`)，**精確地**換算為 `YYYY-MM-DD` 格式。例如，若今天是 2025-08-21 (週四)，「下週三」應換算為 `2025-08-27`。**嚴禁**使用相對時間。

# OUTPUT FORMAT
你「必須」嚴格按照以下 JSON 格式輸出一個操作指令集。這讓後端系統可以安全地執行你的決策。
{{
  "add": {{
    "personal_background": {{ "key": "value" }},
    "health_status": {{ "key": "value" }},
    "life_events": {{ "key": "value" }}
  }},
  "update": {{
    "personal_background": {{ "key": "new_value" }}
  }},
  "remove": ["health_status.some_key.0", "life_events.another_key"]
}}

---
# CONTEXT & IN-CONTEXT LEARNING EXAMPLES

**## 情境輸入 ##**
1.  **既有使用者畫像 (Existing Profile)**: 
    {{profile_data}}
2.  **新的對話摘要 (New Summary)**: 
    {{new_facts}}

---
**## 學習範例 1：新增與更新 ##**
**當前時間**: 2025-08-14
* **既有使用者畫像**:
    ```json
    {{
      "health_status": {{
        "recurring_symptoms": [
          {{"symptom_name": "夜咳", "status": "ongoing", "first_mentioned": "2025-08-01", "last_mentioned": "2025-08-05"}}
        ]
      }}
    }}
    ```
* **新的對話摘要**:
    "使用者情緒不錯，提到女兒美玲下週要帶孫子回來看他，感到很期待。另外，使用者再次抱怨了夜咳的狀況，但感覺比上週好一些。"
* **你的思考**: 新摘要中，「女兒美玲」和「孫子」是新的、重要的家庭成員資訊，應新增為personal_background的家庭資訊。女兒下週帶孫子來訪，應新增為upcoming_events，並將"下週"換算為2025-08-17~2025-08-23。`夜咳` 是既有症狀，應更新 `last_mentioned` 日期。
* **你的輸出**:
    ```json
    {{
      "add": {{
        "personal_background": {{
          "family": {{"daughter_name": "美玲", "has_grandchild": true}}
        }},
        "life_events": {{
          "upcoming_events": [
            {{"event_type": "family_visit", "description": "女兒美玲2025-08-17~2025-08-23帶孫子來訪", "event_date": "2025-08-17~2025-08-23"}}
          ]
      }}
      }},
      "update": {{
        "health_status": {{
          "recurring_symptoms": [
            {{"symptom_name": "夜咳", "status": "ongoing", "first_mentioned": "2025-08-01", "last_mentioned": "2025-08-14"}}
          ]
        }}
      }},
      "remove": []
    }}
    ```

---
**## 學習範例 2：事件結束與狀態變更 ##**
**當前時間**: 2025-08-24
* **既有使用者畫像**:
    ```json
    {{
      "life_events": {{
        "upcoming_events": [
          {{"event_type": "family_visit", "description": "女兒美玲2025-08-17~2025-08-23帶孫子來訪", "event_date": "2025-08-17~2025-08-23"}}
        ]
      }},
      "health_status": {{
        "recurring_symptoms": [
          {{"symptom_name": "夜咳", "status": "ongoing", "first_mentioned": "2025-08-01", "last_mentioned": "2025-08-14"}}
        ]
      }}
    }}
    ```
* **新的對話摘要**:
    "使用者分享了週末和女兒孫子團聚的愉快時光，心情非常好。他還提到，這幾天睡得很好，夜咳的狀況幾乎沒有了。"
* **你的思考**: 「女兒來訪」這個未來事件已經發生，應移除。`夜咳` 狀況已改善，應更新其狀態。
* **你的輸出**:
    ```json
    {{
      "add": {{}},
      "update": {{
        "health_status": {{
          "recurring_symptoms": [
            {{"symptom_name": "夜咳", "status": "resolved", "first_mentioned": "2025-08-01", "last_mentioned": "2025-08-25"}}
          ]
        }}
      }},
      "remove": ["life_events.upcoming_events"]
    }}
    ```

---
**## 你的任務開始 ##**

你的任務:
比較「既有畫像」與「新事實清單」，生成上述格式的 JSON 更新指令。

**當前時間**: 
`{now}`

**既有使用者畫像**: 
`{profile_data}`

**本次對話提煉出的新事實清單**: 
`{new_facts}`

**你的輸出**:
```json
"""

def create_profiler_agent() -> Agent:
    """建立專門用來更新 Profile 的 Agent 物件"""
    return Agent(
        role="個案管理師",
        goal="根據新的對話，決定如何更新既有的使用者畫像，並以結構化的 JSON 指令格式輸出決策。",
        backstory="你是一位經驗豐富、心思縝密的個案管理師，專注於從對話中提取具有長期價值的資訊來維護精簡、準確的使用者畫像。",
        llm=ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"), temperature=0.1), # 使用低溫以確保輸出穩定
        memory=False,
        verbose=False,
        allow_delegation=False
    )


def run_profiler_update(user_id: str, facts: List[Dict[str, Any]]):
    """
    在提煉出 facts 後，觸發 Profiler Agent 來更新使用者畫像。
    """
    if not facts:
        print(f"[Profiler] 事實清單為空，跳過為 user {user_id} 更新 Profile。")
        return

    print(f"[Profiler] 開始為 user {user_id} 更新 Profile...")
    repo = ProfileRepository()
    
    # 1. 獲取舊 Profile
    try:
        user_id_int = int(user_id)
        old_profile = repo.read_profile_as_dict(user_id_int)
        old_profile_str = json.dumps(old_profile, ensure_ascii=False, indent=2) if any(old_profile.values()) else "{}"
    except (ValueError, TypeError) as e:
        print(f"❌ [Profiler] 無效的 user_id '{user_id}'，無法更新 Profile: {e}")
        return
    
    # 2. 建立 Profiler Agent 並執行任務
    profiler_agent = create_profiler_agent()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    facts_str = json.dumps(facts, ensure_ascii=False, indent=2)

    full_prompt = PROFILER_AGENT_PROMPT_TEMPLATE.format(
        now=now_str,
        profile_data=old_profile_str,
        new_facts=facts_str
    )
    
    profiler_task = Task(
        description=full_prompt,
        agent=profiler_agent,
        expected_output="一個包含 'add', 'update', 'remove' 指令的 JSON 物件。"
    )
    
    crew = Crew(
        agents=[profiler_agent],
        tasks=[profiler_task],
        process=Process.sequential,
        verbose=False
    )
    
    crew_output = crew.kickoff()
    update_commands_str = crew_output.raw if crew_output else ""
    
    # 印出 LLM 原始輸出
    print(f"--- [Profiler Raw Output for user {user_id}] ---")
    print(update_commands_str)
    print("------------------------------------------")

    # 3. 解析指令並更新資料庫
    try:
        start_index = update_commands_str.find('{')
        end_index = update_commands_str.rfind('}') + 1
        if start_index == -1 or end_index == 0:
            print(f"[Profiler] LLM 輸出中未找到有效的 JSON 物件，跳過更新。原始輸出: {update_commands_str}")
            return
        
        json_str = update_commands_str[start_index:end_index]
        update_commands = json.loads(json_str)

        if update_commands and any(update_commands.values()):
            repo.update_profile_facts(int(user_id), update_commands)
        else:
            print(f"[Profiler] LLM 為 user {user_id} 回傳了空的更新指令，無需更新。")
            
    except json.JSONDecodeError as e:
        print(f"❌ [Profiler] 解析 LLM 輸出的 JSON 失敗: {e}")
        print(f"原始輸出: {update_commands_str}")
    except Exception as e:
        print(f"❌ [Profiler] 更新 Profile 過程中發生未知錯誤: {e}")


# ========= Finalize：記憶蒸餾 =========
_DISTILL_SYS = """
你是「記憶蒸餾器」。請從本輪對話中，只抽取『可長期重用的既定事實』，並為每一項指定保存期限（TTL）。
抽取規則（務必遵守）：
- 只收：個人背景資訊（如家庭、經歷、喜好）、過敏史、固定偏好、醫囑/用藥（現行）、固定行程/提醒、聯絡人、慢性病史、長期限制/禁忌。
- 不收：寒暄、一次性事件、短期症狀、猜測、模型意見。
- 每項提供 200 字內可讀敘述（display_text），不得添加未出現的推測。
- 每項附 1–3 句【evidence 原話】（逐字引用使用者或助手話語），之後將以此做向量檢索。
- TTL 規則：
  info/allergy/慢性病/聯絡人：ttl_days=0（永久）
  醫囑/用藥：ttl_days=180
  固定偏好：ttl_days=365
  固定行程/提醒：ttl_days=90
  其他長期限制/禁忌：ttl_days=365
- 若無符合，輸出空陣列 []。
輸出 JSON 陣列，元素格式：
{
  "type": "info|allergy|preference|doctor_order|schedule|reminder|contact|condition|constraint|note",
  "display_text": "<200字內可讀敘述>",
  "evidence": ["<原話1>", "<原話2>"],  // 最多3句
  "ttl_days": 0|90|180|365
}
""".strip()


def _distill_facts(user_id: str) -> List[Dict[str, Any]]:
    transcript = _render_session_transcript(user_id)
    if not transcript.strip():
        return []
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    res = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        max_tokens=900,
        messages=[
            {"role": "system", "content": _DISTILL_SYS},
            {
                "role": "user",
                "content": f"使用者本輪對話如下（逐字）：\n<<<\n{transcript}\n>>>",
            },
        ],
    )
    raw = (res.choices[0].message.content or "").strip()
    print(f"\n--- [記憶蒸餾LLM原始輸出: user {user_id}] ---")
    print(raw)
    print("----------------------------------------------------\n")

    # 清掉 ```json 區塊符號
    if raw.startswith("```"):
        lines = [ln for ln in raw.splitlines() if not ln.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    lb, rb = raw.find("["), raw.rfind("]")
    if lb == -1 or rb == -1 or rb <= lb:
        return []
    try:
        arr = json.loads(raw[lb : rb + 1])
        return arr if isinstance(arr, list) else [arr]
    except Exception:
        return []


def _ttl_days_to_expire_at(ttl_days: int) -> int:
    if not ttl_days or int(ttl_days) == 0:
        return 0
    return _now_ms() + int(ttl_days) * 86400 * 1000


def finalize_session(user_id: str) -> None:
    """
    會話收尾：
    1) （可選）補摘要（純為降本，不影響 LTM）
    2) LLM 蒸餾 → 既定事實 + evidence(原話) + ttl_days
    3) 寫入 Milvus：
       - atom：text=display_text；embedding=0 向量；expire_at=由 ttl_days 決定
       - surface：text=原話；embedding=E(原話)；expire_at 同上
    4) 根據蒸餾出的事實更新 Profile
    5) 清理 Redis session
    """
    # 1) 摘要（可註解掉）
    try:
        set_state_if(user_id, expect="ACTIVE", to="FINALIZING")
        start, remaining = peek_remaining(user_id)
        if remaining:
            summarize_chunk_and_commit(
                user_id, start_round=start, history_chunk=remaining
            )
    except Exception as e:
        print(f"[finalize summary warn] {e}")

    # 2) 記憶蒸餾
    facts = _distill_facts(user_id)

    # 3) 入庫
    to_upsert = []
    session_id = f"sess:{int(time.time())}"
    for f in facts:
        display = (f.get("display_text") or "").strip()
        if not display:
            continue
        ttl_days = int(f.get("ttl_days", 365))
        expire_at = _ttl_days_to_expire_at(ttl_days)
        gk = _stable_group_key(display)  # ★ 產生穩定 group_key

        # atom（展示用）
        to_upsert.append(
            {
                "type": "atom",
                "group_key": gk,
                "text": display[:4000],
                "importance": (
                    4
                    if f.get("type")
                    in ("allergy", "doctor_order", "contact", "condition")
                    else 3
                ),
                "confidence": 0.9,
                "times_seen": 1,
                "status": "active",
                "source_session_id": session_id,
                "expire_at": expire_at,
                "embedding": [0.0] * EMBED_DIM,  # 占位，不參與檢索
            }
        )

        # surfaces（檢索主力）：對 evidence 原句做 embedding
        for ev in (f.get("evidence") or [])[:3]:
            ev_txt = (ev or "").strip()
            if not ev_txt:
                continue
            vec = safe_to_vector(ev_txt) or []
            if not vec:
                continue
            to_upsert.append(
                {
                    "type": "surface",
                    "group_key": gk,
                    "text": ev_txt[:4000],
                    "importance": 2,
                    "confidence": 0.95,
                    "times_seen": 1,
                    "status": "active",
                    "source_session_id": session_id,
                    "expire_at": expire_at,
                    "embedding": vec,
                }
            )

    if to_upsert:
        try:
            upsert_atoms_and_surfaces(user_id, to_upsert)
            print(f"✅ finalize：已寫入長期記憶 {len(to_upsert)} 筆（atom/surface）")
        except Exception as e:
            print(f"[finalize upsert error] {e}")
    else:
        print("ℹ️ finalize：本輪沒有可長期保存的事實")

    # 4) 更新 Profile
    # 使用第 2 步產生的 facts 來更新 Profile
    run_profiler_update(user_id, facts)

    # 5) 清理 session
    try:
        cleanup_session_keys(user_id)
    except Exception as e:
        print(f"[finalize purge warn] {e}")


# ========= CrewAI 代理工廠（供 chat_pipeline 匯入）=========
def create_guardrail_agent() -> Agent:
    return Agent(
        role="Guardrail",
        goal="判斷是否需要攔截使用者輸入（安全/法律/醫療等高風險）",
        backstory="嚴謹的安全審查器",
        tools=[ModelGuardrailTool()],
        verbose=False,
        allow_delegation=False,
        llm=guard_llm,
        memory=False,
    )


def create_health_companion(user_id: str) -> Agent:
    return Agent(
        role="National Granddaughter Ally",
        goal="溫暖陪伴並給一行回覆；工具僅在符合當輪規則時使用，避免不必要的查詢與通報。",
        backstory=f"陪伴使用者 {user_id} 的溫暖孫女",
        tools=[
            SearchMilvusTool(),
            AlertCaseManagerTool(),
        ],  # 緊急時會被任務 prompt 要求觸發
        verbose=False,
        allow_delegation=False,
        llm=granddaughter_llm,
        memory=False,
        max_iterations=1,
    )
