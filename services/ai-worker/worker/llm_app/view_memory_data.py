#!/usr/bin/env python3
# view_memory_data.py  (v3 schema viewer + live search)

import json
import os
import time
import sys
from typing import List

import redis
from pymilvus import Collection, connections
# 嘗試使用專案的 embedding.safe_to_vector；若失敗，改用 OpenAI
try:
    sys.path.append(os.path.dirname(__file__) or ".")
    from embedding import safe_to_vector
    def embed(text: str) -> List[float]:
        return safe_to_vector(text) or []
except Exception:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-3-small")
    def embed(text: str) -> List[float]:
        r = _client.embeddings.create(model=_EMB_MODEL, input=text)
        return r.data[0].embedding

MEM_COLLECTION = os.getenv("MEMORY_COLLECTION", "user_memory_v3")
MILVUS_HOSTS = [("localhost", 19530), ("milvus", 19530), ("127.0.0.1", 19530)]
REDIS_HOSTS = [("localhost", 6379), ("redis", 6379), ("127.0.0.1", 6379)]


def get_redis_client():
    for host, port in REDIS_HOSTS:
        try:
            client = redis.Redis(host=host, port=port, decode_responses=True)
            client.ping()
            print(f"✅ Redis 已連線: {host}:{port}")
            return client
        except Exception as e:
            print(f"❌ Redis 連線失敗: {host}:{port} {e}")
    raise RuntimeError("無法連線 Redis")


def connect_milvus():
    for host, port in MILVUS_HOSTS:
        try:
            connections.connect(alias="default", host=host, port=port)
            print(f"✅ Milvus 已連線: {host}:{port}")
            return
        except Exception as e:
            print(f"❌ Milvus 連線失敗: {host}:{port} {e}")
    raise RuntimeError("無法連線 Milvus")


def fmt_ts(ms: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ms/1000)) if ms else "N/A"


def view_milvus_user(collection, user_id: str):
    now = int(time.time()*1000)
    rows = collection.query(
        expr=f'user_id == "{user_id}"',
        limit=5000,
        output_fields=["pk","user_id","type","group_key","status","created_at","updated_at","last_used_at","expire_at","importance","text"]
    )
    if not rows:
        print(f"📝 無 {user_id} 資料")
        return

    # 依 group_key 聚合顯示
    groups = {}
    for r in rows:
        groups.setdefault(r["group_key"], []).append(r)

    print(f"📦 總筆數：{len(rows)}，群組數：{len(groups)}")
    for gk, items in groups.items():
        items_sorted = sorted(items, key=lambda x: (x["type"]!="atom", -(x["updated_at"] or 0)))
        head = items_sorted[0]
        alive = (head.get("expire_at", 0) == 0) or (head.get("expire_at", 0) >= now)
        flag = "🟢" if alive and head["status"]=="active" else "⚫"
        print(f"\n{flag} group_key={gk}  status={head['status']}  expire_at={fmt_ts(head.get('expire_at',0))}")
        for r in items_sorted:
            print(f"   - [{r['type']}] pk={r['pk']} imp={r.get('importance',0)} "
                  f"created={fmt_ts(r.get('created_at',0))} last_used={fmt_ts(r.get('last_used_at',0))}")
            txt = (r.get("text") or "").replace("\n"," / ")
            print(f"     ⤷ {txt[:160]}{'...' if len(txt)>160 else ''}")


def delete_milvus_user(collection, user_id: str):
    rows = collection.query(expr=f'user_id == "{user_id}"', output_fields=["pk"], limit=10000)
    if not rows:
        print("📝 無資料可刪")
        return
    pks = ",".join(str(r["pk"]) for r in rows)
    collection.delete(expr=f"pk in [{pks}]")
    collection.flush()
    print(f"✅ 已刪除 {len(rows)} 筆 Milvus 記錄")


def view_redis_user(r, user_id: str):
    patterns = [f"session:{user_id}:*", f"audio:{user_id}:*", f"processed:{user_id}:*"]
    keys = set()
    for pat in patterns:
        keys.update(r.keys(pat))
    if not keys:
        print(f"📝 無 {user_id} Redis 資料")
        return
    for k in sorted(keys):
        dtype = r.type(k)
        print(f"\n🔑 {k} ({dtype})")
        if dtype == "string":
            print(r.get(k))
        elif dtype == "list":
            lst = r.lrange(k, 0, -1)
            print(lst[:5], "..." if len(lst)>5 else "")
        elif dtype == "stream":
            print(r.xrange(k, count=5))
        else:
            print("(未處理類型)")


def delete_redis_user(r, user_id: str):
    patterns = [f"session:{user_id}:*", f"audio:{user_id}:*", f"processed:{user_id}:*"]
    total = 0
    for pat in patterns:
        ks = r.keys(pat)
        if ks:
            total += r.delete(*ks)
    print(f"✅ 已刪除 {total} 個 Redis 項")


def live_search(collection, user_id: str, query: str, topk: int = 5):
    vec = embed(query)
    now = int(time.time()*1000)
    expr = f'user_id == "{user_id}" and status == "active" and (expire_at == 0 or expire_at >= {now})'
    res = collection.search(
        data=[vec],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"ef": 128}},
        limit=max(20, topk*4),
        expr=expr,
        output_fields=["pk","type","group_key","text","expire_at","last_used_at","importance"]
    )
    hits = res[0]
    if not hits:
        print("（無命中）")
        return
    print(f"\n🔍 Query: {query}")
    print("TOP 命中：")
    shown = 0
    for h in hits:
        # score/distance 兼容
        sim = float(getattr(h, "distance", getattr(h, "score", 0.0)))
        if shown >= topk:
            break
        e = h.entity
        print(f"- score={sim:.3f}  type={e.get('type')}  gk={e.get('group_key')}  expire_at={fmt_ts(e.get('expire_at',0))}")
        txt = (e.get("text") or "").replace("\n"," / ")
        print(f"  ⤷ {txt[:180]}{'...' if len(txt)>180 else ''}")
        shown += 1


def main():
    connect_milvus()
    coll = Collection(MEM_COLLECTION); coll.load()
    r = get_redis_client()
    print("指令：")
    print("  m <uid>            查看 Milvus v3（依 group_key 聚合）")
    print("  mq <uid> <query>   用向量搜尋看看 Top 命中（active & 未過期）")
    print("  mr <uid>           查看 Redis")
    print("  d <uid>            刪除該 uid 的 Milvus + Redis")
    print("  exit               離開")
    while True:
        try:
            cmd = input("db> ").strip()
        except EOFError:
            break
        if not cmd: 
            continue
        if cmd == "exit":
            break
        parts = cmd.split()
        if parts[0] == "m" and len(parts) > 1:
            view_milvus_user(coll, parts[1])
        elif parts[0] == "mq" and len(parts) > 2:
            uid = parts[1]; q = " ".join(parts[2:])
            live_search(coll, uid, q)
        elif parts[0] == "mr" and len(parts) > 1:
            view_redis_user(r, parts[1])
        elif parts[0] == "d" and len(parts) > 1:
            delete_milvus_user(coll, parts[1]); delete_redis_user(r, parts[1])
        else:
            print("未知指令")
if __name__ == "__main__":
    main()
