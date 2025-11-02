import json
import os
from typing import Dict, List, Type

from crewai.tools import BaseTool
from openai import OpenAI
from pydantic import BaseModel, Field
from pymilvus import Collection, connections

from ..embedding import to_vector
from .redis_store import commit_summary_chunk

_milvus_loaded = False
_collection = None


class MemoryGateToolSchema(BaseModel):
    text: str = Field(..., description="使用者本輪輸入")


class MemoryGateTool(BaseTool):
    name: str = "memory_gate"
    description: str = "判斷是否需要檢索個人長期記憶。只輸出 USE 或 SKIP。"
    args_schema: Type[BaseModel] = MemoryGateToolSchema

    def _run(self, text: str) -> str:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            sys = (
                "你是決策器。若輸入涉及個人既往事實/偏好/限制/用藥/醫囑/排程/家人稱呼/上一輪內容的指涉，"
                "或出現『上次/之前/一樣/那個/還是/不要/過敏/醫師說/固定/提醒』等字眼，回 USE；"
                "否則回 SKIP。只輸出 USE 或 SKIP。"
            )
            res = client.chat.completions.create(
                model=os.getenv("GUARD_MODEL", os.getenv("MODEL_NAME", "gpt-4o-mini")),
                temperature=0,
                max_tokens=4,
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": text},
                ],
            )
            out = (res.choices[0].message.content or "").strip().upper()
            return "USE" if out.startswith("USE") else "SKIP"
        except Exception:
            # 失敗時保守：直接 SKIP，避免卡流程
            return "SKIP"


_milvus_loaded = False
_collection = None


def _index_type_of(col: Collection) -> str:
    idx = (col.indexes or [None])[0]
    it = (idx and idx.params.get("index_type")) or ""
    if not it and idx and isinstance(idx.params.get("params"), str):
        try:
            it = json.loads(idx.params["params"]).get("index_type", "")
        except Exception:
            pass
    return (it or "HNSW").upper()


def _search_param(idx_type: str) -> Dict:
    if idx_type.startswith("IVF"):
        return {
            "metric_type": "COSINE",
            "params": {"nprobe": int(os.getenv("COPD_NPROBE", 32))},
        }
    return {"metric_type": "COSINE", "params": {"ef": int(os.getenv("COPD_EF", 128))}}


class SearchMilvusToolSchema(BaseModel):
    query: str = Field(
        ..., description="當前要查詢的自然語句（使用者提問或你轉述的關鍵句）"
    )
    topk: int = Field(5, description="最多擷取的候選數量（預設5）")


class SearchMilvusTool(BaseTool):
    name: str = "search_milvus"
    description: str = (
        "檢索 COPD 教育與衛教問答資料庫。當你需要客觀知識（如疾病概念、症狀、風險、就醫時機、"
        "生活衛教、自我照護等）或你對答案來源不確定時，先呼叫本工具。工具會回傳一段可直接拼入"
        "提示詞的『參考資料』區塊，內含相似度最高的一筆 Q&A 與使用說明，供你理解並轉述整合。"
    )
    args_schema: Type[BaseModel] = SearchMilvusToolSchema

    def _run(self, query: str, topk: int = 5) -> str:
        global _milvus_loaded, _collection
        try:
            if not _milvus_loaded:
                try:
                    connections.get_connection("default")
                except Exception:
                    connections.connect(
                        alias="default",
                        uri=os.getenv("MILVUS_URI", "http://localhost:19530"),
                    )
                coll_name = os.getenv("COPD_COLL_NAME", "copd_qa")
                _collection = Collection(coll_name)
                _collection.load()
                _milvus_loaded = True

            vec = to_vector(query)
            if not vec:
                return json.dumps({"source": "copd_qa", "hits": []}, ensure_ascii=False)
            if not isinstance(vec, list):
                vec = vec.tolist() if hasattr(vec, "tolist") else list(vec)

            idx_type = _index_type_of(_collection)
            param = _search_param(idx_type)
            res = _collection.search(
                data=[vec],
                anns_field="embedding",
                param=param,
                limit=topk,
                output_fields=["question", "answer", "category", "keywords", "notes"],
            )

            thr = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
            hits: List[dict] = []
            for h in res[0]:
                score = float(getattr(h, "distance", getattr(h, "score", 0.0)))
                if score >= thr:
                    e = h.entity
                    hits.append(
                        {
                            "score": score,
                            "q": e.get("question", ""),
                            "a": e.get("answer", ""),
                            "cat": e.get("category", ""),
                            "kw": e.get("keywords", ""),
                            "notes": e.get("notes", ""),
                        }
                    )
            if not hits:
                return (
                    "📚 參考資料：未找到相符條目（可能無資料或相似度不足）。"
                    "若你仍需回答，請基於通用常識與目前對話脈絡，簡潔回覆；避免杜撰。"
                )

            # 取相似度最高一筆
            best = max(hits, key=lambda x: x.get("score", 0.0))
            score_txt = f"{best.get('score', 0.0):.3f}"
            q = (best.get("q") or "").strip()
            a = (best.get("a") or "").strip()

            # 回傳可直接嵌入 LLM 提示的區塊，並附上使用說明
            return (
                "📚 參考資料（Milvus COPD QA，已挑相似度最高一筆；metric=COSINE；score="
                + score_txt
                + ")：\n"
                + ("Q: " + q + "\n" if q else "")
                + ("A: " + a + "\n" if a else "")
                + "使用方式：將 A 的重點轉述為自然口語並結合當前脈絡；若不相符或過時，請忽略。不要逐字貼上或外洩敏感資訊。"
            )
        except Exception as e:
            return f"📚 參考資料：檢索失敗（{str(e)}）。若你仍需回答，請基於通用常識與目前脈絡，簡潔回覆；避免杜撰。"


def summarize_chunk_and_commit(
    user_id: str, start_round: int, history_chunk: list
) -> bool:
    if not history_chunk:
        return True
    text = "".join(
        [
            f"第{start_round + i + 1}輪:\n長輩: {h['input']}\n金孫: {h['output']}\n\n"
            for i, h in enumerate(history_chunk)
        ]
    )
    prompt = f"請將下列對話做 80-120 字摘要，聚焦：健康問題、情緒、生活要點。\n\n{text}"
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "你是專業的對話摘要助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        body = (res.choices[0].message.content or "").strip()
        header = f"--- 第{start_round + 1}至{start_round + len(history_chunk)}輪對話摘要 ---\n"
        return commit_summary_chunk(
            user_id,
            expected_cursor=start_round,
            advance=len(history_chunk),
            add_text=header + body,
        )
    except Exception as e:
        print(f"[摘要錯誤] {e}")
        return False


class AlertCaseManagerToolSchema(BaseModel):
    reason: str = Field(
        ...,
        description="一行原因字串，需以 'EMERGENCY:' 開頭，例如：'EMERGENCY: suicidal ideation'",
    )


class AlertCaseManagerTool(BaseTool):
    name: str = "alert_case_manager"
    description: str = (
        "偵測到緊急健康/心理風險時，立即通報個管師。"
        "【用法】以 JSON 傳入 {'reason': 'EMERGENCY: <極簡原因>'}；"
        "用戶ID由系統自動填入，無需提供。"
    )
    args_schema: Type[BaseModel] = AlertCaseManagerToolSchema  # ★ 關鍵：明確宣告參數鍵

    def _run(self, reason: str) -> str:
        # 安全地抓 user_id；CrewAI 預設沒有 runtime_context
        uid = None
        try:
            uid = (getattr(self, "runtime_context", {}) or {}).get("user_id")
        except Exception:
            pass
        uid = uid or os.getenv("CURRENT_USER_ID") or "unknown"

        from datetime import datetime

        ts = datetime.now().isoformat(timespec="seconds")
        print(f"[{ts}] 🚨 AlertCaseManagerTool triggered: user={uid}, reason={reason}")
        # 這裡本來有 MQ 發送的註解碼，保留即可
        from .rabbitmq_publisher import publish_alert
        publish_alert(user_id=uid, reason=reason)
        return f"⚠️ 已通報個管師使用者ID: {uid}，事由：{reason}"


class ModelGuardrailTool(BaseTool):
    name: str = "model_guardrail"
    description: str = (
        "完全由 LLM 安全審查：判斷是否違法/危險/自傷，或屬於需專業人士的具體指示（如用藥/劑量/診斷/處置）。只輸出 OK 或 BLOCK: <原因>。"
    )

    def _run(self, text: str) -> str:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            guard_model = os.getenv(
                "GUARD_MODEL", os.getenv("MODEL_NAME", "gpt-4o-mini")
            )
            sys = (
                "你是安全審查器，需精準判斷是否必須攔截。\n"
                "【允許（回 OK）】以下情況一律放行：\n"
                "- 症狀敘述或一般健康資訊的詢問（例如：症狀、成因、風險因子、何時就醫的提醒）。\n"
                "- 一般生活保健/衛教/注意事項等非個案化、非指令性的建議。\n"
                "- 情緒低落、自殺念頭或求助的表達（不含具體方法）。\n"
                "【必須攔截（回 BLOCK: <原因>）】符合任一條件：\n"
                "1) 違法/危險行為的教學、買賣、製作或規避（毒品、武器、暴力、駭客、爆裂物等）。\n"
                "2) 自傷/他傷/自殺/自殘的『具體方法指導或鼓勵執行』。\n"
                "3) 成人性內容或未成年相關不當內容的請求。\n"
                "4) 醫療/用藥/劑量/診斷/處置等『具體、個案化、可執行』的專業指示或方案。\n"
                "5) 法律、投資、稅務等高風險領域之『具體、可執行』的專業指導。\n"
                "【判斷原則】僅在請求明確落入上述攔截條件時才 BLOCK；\n"
                "若是描述狀況或尋求一般性說明/保健建議，請回 OK。\n"
                "若不確定，預設回 OK。\n"
                "【輸出格式】只能是：\n"
                "OK\n"
                "或\n"
                "BLOCK: <極簡原因>\n"
            )

            user = f"使用者輸入：{text}\n請依規則只輸出 OK 或 BLOCK: <原因>。"
            res = client.chat.completions.create(
                model=guard_model,
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                max_tokens=24,
            )
            out = (res.choices[0].message.content or "").strip()
            # 預設寬鬆通過：若非明確 BLOCK，一律視為 OK
            if not out.startswith("BLOCK:"):
                return "OK"
            # 僅保留精簡 BLOCK 理由
            if len(out) > 256:
                out = out[:256]
            return out
        except Exception as e:
            # Guardrail 故障時，不要阻擋主流程
            print(f"[guardrail_error] {e}")
            return "OK"
