# -*- coding: utf-8 -*-
# file: toolkits/memory_store.py  ← 直接用這份覆蓋
import hashlib
import math
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from pymilvus import (
    Collection, CollectionSchema, DataType, FieldSchema, connections, utility
)

EMBED_DIM = int(os.getenv("EMBED_DIM", 1536))  # text-embedding-3-small = 1536
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COLL = os.getenv("MEMORY_COLLECTION", "user_memory_v3")

_cached_collection = None
_loaded = False


def _connect():
    try:
        connections.get_connection("default")
    except Exception:
        connections.connect(alias="default", uri=MILVUS_URI)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def _pk_for_atom(user_id: str, group_key: str) -> int:
    h = hashlib.sha1(f"{user_id}|atom|{group_key}".encode()).digest()
    return int.from_bytes(h[:8], "big", signed=False) & ((1 << 63) - 1)


def _pk_for_surface(user_id: str, group_key: str, text: str) -> int:
    # 每句 evidence 一個穩定 pk（text 取前 80 字避免過長）
    h = hashlib.sha1(f"{user_id}|surface|{group_key}|{text[:80]}".encode()).digest()
    return int.from_bytes(h[:8], "big", signed=False) & ((1 << 63) - 1)


def _pk_for_rawqa(user_id: str, text: str) -> int:
    h = hashlib.sha1(f"{user_id}|raw_qa|{text[:80]}".encode()).digest()
    return int.from_bytes(h[:8], "big", signed=False) & ((1 << 63) - 1)


def ensure_memory_collection() -> Collection:
    global _cached_collection, _loaded
    if _cached_collection and _loaded:
        return _cached_collection
    _connect()
    if utility.has_collection(COLL):
        c = Collection(COLL)
        # 對齊向量維度
        try:
            for f in c.schema.fields:
                if f.name == "embedding" and hasattr(f, "params") and "dim" in f.params:
                    global EMBED_DIM
                    if EMBED_DIM != f.params["dim"]:
                        EMBED_DIM = f.params["dim"]
                        print(f"⚠️ EMBED_DIM 校正為 {EMBED_DIM}")
        except Exception:
            pass
        if not _loaded:
            try:
                c.load()
                _loaded = True
            except Exception:
                pass
        _cached_collection = c
        return c

    # 新 schema：atom/surface/raw_qa + expire_at
    fields = [
        FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=16),  # atom/surface/raw_qa
        FieldSchema(name="group_key", dtype=DataType.VARCHAR, max_length=128),  # 自動 hash
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="importance", dtype=DataType.INT64),
        FieldSchema(name="confidence", dtype=DataType.FLOAT),
        FieldSchema(name="times_seen", dtype=DataType.INT64),
        FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=16),  # active/archived/superseded
        FieldSchema(name="source_session_id", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="created_at", dtype=DataType.INT64),
        FieldSchema(name="updated_at", dtype=DataType.INT64),
        FieldSchema(name="last_used_at", dtype=DataType.INT64),
        FieldSchema(name="expire_at", dtype=DataType.INT64),  # 0=永久
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBED_DIM),
    ]
    schema = CollectionSchema(fields, description="Personal long-term memory v3 (atom/surface/raw_qa)")
    c = Collection(COLL, schema=schema)
    c.create_index(
        field_name="embedding",
        index_params={
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 16, "efConstruction": 200},
        },
    )
    c.load()
    _cached_collection = c
    _loaded = True
    return c


def upsert_atoms_and_surfaces(user_id: str, items: List[Dict[str, Any]]) -> int:
    """
    items: 每筆必含 type in {'atom','surface','raw_qa'}, text, （可選）group_key, importance, confidence,
           times_seen, status, source_session_id, created_at/updated_at/last_used_at, expire_at, embedding
    - atom: 建議 embedding 可省略（None/[]），需要時可加備援
    - surface/raw_qa: 必須有 embedding（用原句向量）
    """
    if not items:
        return 0
    c = ensure_memory_collection()
    now = _now_ms()
    rows = {k: [] for k in [
        "pk","user_id","type","group_key","text","importance","confidence","times_seen",
        "status","source_session_id","created_at","updated_at","last_used_at","expire_at","embedding"
    ]}
    for a in items:
        t = a.get("type")
        if t not in ("atom","surface","raw_qa"):
            raise ValueError("type 必須為 atom/surface/raw_qa")
        text = (a.get("text") or "")[:4000]
        gk = (a.get("group_key") or "")
        if t == "atom":
            # 未提供 group_key 時，直接用展示文本 hash 做穩定鍵
            gk = gk or ("auto:" + _sha1(text.lower())[:32])
            pk = _pk_for_atom(user_id, gk)
        elif t == "surface":
            if not gk:
                raise ValueError("surface 需要 group_key（對齊對應 atom）")
            pk = _pk_for_surface(user_id, gk, text)
        else:  # raw_qa
            pk = _pk_for_rawqa(user_id, text)

        emb = a.get("embedding") or []
        if t != "atom":
            # surface/raw_qa 一定要有 embedding
            if not isinstance(emb, list) or len(emb) != EMBED_DIM:
                raise ValueError(f"{t} 需要 embedding（dim={EMBED_DIM}）")
        else:
            # atom 若沒 embedding 可以塞空向量（Milvus 要求維度一致；這裡給全 0 做 placeholder）
            if not emb or len(emb) != EMBED_DIM:
                emb = [0.0] * EMBED_DIM

        rows["pk"].append(pk)
        rows["user_id"].append(user_id)
        rows["type"].append(t)
        rows["group_key"].append(gk)
        rows["text"].append(text)
        rows["importance"].append(int(a.get("importance", 3)))
        rows["confidence"].append(float(a.get("confidence", 0.9 if t=="surface" else 0.8)))
        rows["times_seen"].append(int(a.get("times_seen", 1)))
        rows["status"].append(a.get("status","active"))
        rows["source_session_id"].append(a.get("source_session_id",""))
        rows["created_at"].append(int(a.get("created_at", now)))
        rows["updated_at"].append(int(a.get("updated_at", now)))
        rows["last_used_at"].append(int(a.get("last_used_at", now)))
        rows["expire_at"].append(int(a.get("expire_at", 0)))
        rows["embedding"].append(emb)

    c.upsert([rows[k] for k in [
        "pk","user_id","type","group_key","text","importance","confidence","times_seen",
        "status","source_session_id","created_at","updated_at","last_used_at","expire_at","embedding"
    ]])
    return len(rows["pk"])


def _recency_weight(ts_ms: int, tau_days: int = 45) -> float:
    if not ts_ms:
        return 0.0
    delta_days = max(0.0, (time.time() * 1000 - ts_ms) / 86400000.0)
    return math.exp(-delta_days / float(tau_days))


def retrieve_memory_pack_v3(
    user_id: str, query_vec: List[float], topk_groups: int = 5,
    sim_thr: Optional[float] = None, tau_days: int = 45, include_raw_qa: bool = False
) -> str:
    c = ensure_memory_collection()
    now = _now_ms()

    # 門檻可由環境變數覆蓋；若傳入為 None 則讀 ENV，預設 0.38
    sim_thr = float(os.getenv("MEM_SIM_THR", "0.5")) if (sim_thr is None) else float(sim_thr)

    # ✅ Milvus 的 in 子句需使用方括號
    type_filter = '["surface","atom"]' if not include_raw_qa else '["surface","atom","raw_qa"]'
    expr = (
        f'user_id == "{user_id}" and status == "active" and '
        f'(expire_at == 0 or expire_at >= {now}) and type in {type_filter}'
    )

    res = c.search(
        data=[query_vec],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"ef": 128}},
        limit=50,
        expr=expr,
        output_fields=["pk","type","group_key","text","importance","times_seen","last_used_at"]
    )

    def _score_of(h):
        return float(getattr(h, "distance", getattr(h, "score", 0.0)))

    hits = [h for h in res[0] if _score_of(h) >= sim_thr]
    # 命中為空時，就地放寬一次（不重打 DB）
    if not hits and res and len(res[0]) > 0:
        relax_thr = max(0.30, sim_thr * 0.7)
        hits = [h for h in res[0] if _score_of(h) >= relax_thr]

    if not hits:
        return ""

    # 以 group_key 聚合；surface 命中權重較高
    buckets: Dict[str, Dict[str, Any]] = {}
    for h in hits:
        e = h.entity
        gk = e.get("group_key") or "rawqa:"+_sha1(e.get("text") or "")
        t = e.get("type")
        sim = _score_of(h)
        rec = _recency_weight(int(e.get("last_used_at") or 0), tau_days)
        imp = (int(e.get("importance") or 3))/5.0
        base = 0.64*sim + 0.18*rec + 0.12*imp
        bonus = 0.05 if t == "surface" else 0.0
        score = base + bonus
        b = buckets.setdefault(gk, {"score":-1,"best_surface":None,"best_atom":None})
        if score > b["score"]:
            b["score"] = score
        if t == "surface" and (b["best_surface"] is None):
            b["best_surface"] = e
        if t == "atom":
            b["best_atom"] = e

    order = sorted(buckets.items(), key=lambda kv: kv[1]["score"], reverse=True)[:max(1,topk_groups)]

    lines = []
    update_rows = []
    for gk, info in order:
        atom = info["best_atom"]
        surf = info["best_surface"]
        if atom is not None:
            lines.append(f'- {atom.get("text")}')
            update_rows.append(("atom", atom))
        elif surf is not None:
            lines.append(f'- {surf.get("text")}（原話）')
            update_rows.append(("surface", surf))

    # ✅ 命中統計：顯式帶出需要的欄位，避免 'user_id' KeyError
    try:
        if update_rows:
            for t, e in update_rows:
                pk = e.get("pk")
                if not pk:
                    continue
                full = c.query(
                    expr=f"pk in [{pk}]",
                    output_fields=[
                        "pk","user_id","type","group_key","text","importance","confidence",
                        "times_seen","status","source_session_id","created_at","updated_at",
                        "last_used_at","expire_at","embedding",
                    ],
                )
                if not full:
                    continue
                row = full[0]
                c.upsert([[row["pk"]],[row["user_id"]],[row["type"]],[row["group_key"]],
                          [row["text"]],[row["importance"]],[row["confidence"]],
                          [int(row.get("times_seen",1))+1],[row["status"]],
                          [row["source_session_id"]],[row["created_at"]],
                          [_now_ms()],[ _now_ms() ],[row.get("expire_at",0)],[row["embedding"]]])
    except Exception as ex:
        print(f"[usage update warn] {ex}")

    return "⭐ 個人長期記憶：\n" + "\n".join(lines) if lines else ""



def gc_expired(user_id: Optional[str] = None, hard_delete: bool = False) -> int:
    """封存或刪除過期記憶；回傳影響筆數（估算）。"""
    c = ensure_memory_collection()
    now = _now_ms()
    base = f'(expire_at != 0 and expire_at < {now})'
    if user_id:
        base = f'user_id == "{user_id}" and ' + base
    rows = c.query(expr=base, output_fields=["pk"])
    if not rows:
        return 0
    pks = ",".join(str(r["pk"]) for r in rows)
    if hard_delete:
        c.delete(expr=f"pk in [{pks}]")
    else:
        # 軟封存：狀態變 archived（仍保留資料）
        full = c.query(expr=f"pk in [{pks}]", output_fields=None)
        if full:
            c.upsert([
                [r["pk"] for r in full],
                [r["user_id"] for r in full],
                [r["type"] for r in full],
                [r["group_key"] for r in full],
                [r["text"] for r in full],
                [r["importance"] for r in full],
                [r["confidence"] for r in full],
                [r["times_seen"] for r in full],
                ["archived"] * len(full),
                [r["source_session_id"] for r in full],
                [r["created_at"] for r in full],
                [_now_ms()] * len(full),
                [r["last_used_at"] for r in full],
                [r["expire_at"] for r in full],
                [r["embedding"] for r in full],
            ])
    return len(rows or [])


def get_recent_memories(user_id: str, topk: int = 5, days_limit: int = 7) -> str:
    """
    主動關懷專用函式。
    不進行語意搜尋，而是直接獲取指定天數內、最新的 topk 筆記憶。
    """
    print(f"🔍 正在為 user_id={user_id} 檢索最近 {days_limit} 天內的記憶...")
    c = ensure_memory_collection()
    
    # 1. 計算時間範圍
    now_ts_ms = int(time.time() * 1000)
    start_ts_ms = now_ts_ms - int(timedelta(days=days_limit).total_seconds() * 1000)
    
    # 2. 建立查詢表達式
    expr = f'user_id == "{user_id}" and created_at >= {start_ts_ms} and type == "atom"'
    
    try:
        # 3. 執行查詢
        # 先取出一個稍大的數量，然後在 Python 中排序
        results = c.query(
            expr=expr,
            output_fields=["text", "created_at"],
            limit=100 # 取出近期最多100筆以供排序
        )
        
        if not results:
            print(f"❌ 用戶 {user_id} 在最近 {days_limit} 天內沒有可檢索的記憶。")
            return ""
            
        # 4. 在 Python 端進行排序，並選取 topk
        # 按照 created_at 降序排列 (最新的在前面)
        sorted_results = sorted(results, key=lambda r: r['created_at'], reverse=True)
        top_results = sorted_results[:topk]
        
        # 5. 格式化輸出
        lines = [f'- {item["text"]}' for item in top_results]
        
        # 反轉順序，讓最早的記憶在最前面，符合對話時序
        lines.reverse() 
        
        formatted_string = "\n".join(lines)
        print(f"🧠 為用戶 {user_id} 檢索到 {len(top_results)} 筆近期記憶。")
        return formatted_string
        
    except Exception as e:
        print(f"[get_recent_memories error] 檢索近期記憶時發生錯誤: {e}")
        return ""
