# -*- coding: utf-8 -*-
import hashlib
import json
import os
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import redis
from ..repositories.profile_repository import ProfileRepository

ALERT_STREAM_KEY = os.getenv("ALERT_STREAM_KEY", "alerts:stream")
ALERT_STREAM_GROUP = os.getenv("ALERT_STREAM_GROUP", "case_mgr")

# 對話閒置超過此時間則視為結束，觸發收尾流程
SESSION_TIMEOUT_SECONDS = 300

@lru_cache(maxsize=1)
def get_redis() -> redis.Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url, decode_responses=True)

def start_or_refresh_session(user_id: str, line_user_id: str = None) -> None:
    """
    啟動一個新 Session 或刷新既有 Session 的過期時間。
    只有在 Session 是新啟動時，才會更新資料庫的 last_contact_ts。
    """
    r = get_redis()
    active_key = f"session:active:{user_id}"
    last_active_key = f"session:last_active:{user_id}"

    # 檢查是否為新 Session
    is_new_session = not r.exists(active_key)

    # 使用 pipeline 確保原子性
    with r.pipeline() as pipe:
        # 1. 設置或刷新活躍標記，TTL 為 5 分鐘
        pipe.set(active_key, "1", ex=SESSION_TIMEOUT_SECONDS)
        
        # 2. 更新最後活躍時間戳 (永不過期，供排程任務掃描)
        pipe.set(last_active_key, int(time.time()))
        
        pipe.execute()

    # 如果是新 Session，才更新 last_contact_ts
    if is_new_session:
        try:
            repo = ProfileRepository()
            # 只有在 line_user_id 有效時才傳遞，避免用 None 覆蓋舊值
            if line_user_id:
                repo.touch_last_contact_ts(int(user_id), line_user_id=line_user_id)
            else:
                repo.touch_last_contact_ts(int(user_id))
            print(f"✨ 啟動新 session：user_id = {user_id}. 'last_contact_ts'已更新.")
        except (ValueError, TypeError):
            # 如果 user_id 不是一個有效的數字字串，則跳過對資料庫的操作，避免崩潰。
            print(f"⚠️ [Session 啟動] user_id '{user_id}' 不是有效的整數，已跳過 'last_contact_ts' 更新。")
    
    print(f"🔄 Session for user {user_id} has been {'started' if is_new_session else 'refreshed'}.")


def is_session_active(user_id: str) -> bool:
    """檢查使用者的 Session 當前是否活躍"""
    r = get_redis()
    return bool(r.exists(f"session:active:{user_id}"))


def get_expired_sessions(timeout_seconds: int = SESSION_TIMEOUT_SECONDS) -> List[str]:
    """
    排程任務將呼叫此函式，掃描所有使用者的最後活躍時間，找出已過期的 Session。
    """
    r = get_redis()
    # 使用 SCAN 避免在大量用戶時阻塞 Redis
    cursor = '0'
    expired_users = []
    now = int(time.time())
    
    while cursor != 0:
        cursor, keys = r.scan(cursor=cursor, match="session:last_active:*", count=100)
        if not keys:
            continue
        
        last_active_times = r.mget(keys)
        for i, key in enumerate(keys):
            try:
                # 從 "session:last_active:USER_ID" 中提取 USER_ID
                user_id = key.split(':')[-1]
                last_active_time = last_active_times[i]
                if last_active_time and (now - int(last_active_time) > timeout_seconds):
                    # 檢查 active key 是否也真的消失了，雙重確認
                    if not is_session_active(user_id):
                        expired_users.append(user_id)
            except (IndexError, ValueError, AttributeError):
                # 處理潛在的鍵格式錯誤或類型錯誤
                print(f"⚠️ 無法處理 Redis key: {key}")
                continue
    return expired_users

def cleanup_session_keys(user_id: str) -> None:
    """在 finalize_session 後，清除所有 session 相關的 key"""
    r = get_redis()
    # 使用 scan 找到所有相關 key，避免硬編碼
    keys_to_delete = []
    for key in r.scan_iter(match=f"session:{user_id}:*"):
        keys_to_delete.append(key)
    for key in r.scan_iter(match=f"session:active:{user_id}"):
        keys_to_delete.append(key)
    for key in r.scan_iter(match=f"session:last_active:{user_id}"):
        keys_to_delete.append(key)

    if keys_to_delete:
        r.delete(*keys_to_delete)
        print(f"🧹 user {user_id} 的所有 session keys 已清除。")



def try_register_request(user_id: str, request_id: str) -> bool:
    r = get_redis()
    key = f"processed:{user_id}:{request_id}"
    return bool(r.set(key, "1", nx=True, ex=SESSION_TIMEOUT_SECONDS * 2))


def make_request_id(user_id: str, text: str, now_ms: Optional[int] = None) -> str:
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    bucket = now_ms // 3000
    return hashlib.sha1(f"{user_id}|{text}|{bucket}".encode()).hexdigest()


def append_round(user_id: str, round_obj: Dict, line_user_id: str = None) -> None:
    r = get_redis()
    key = f"session:{user_id}:history"
    r.rpush(key, json.dumps(round_obj, ensure_ascii=False))
    start_or_refresh_session(user_id, line_user_id=line_user_id)

# 主動關懷專用函式
def append_proactive_round(user_id: str, round_obj: Dict) -> None:
    """專門用於寫入主動關懷訊息，但不重置閒置計時器。"""
    r = get_redis()
    key = f"session:{user_id}:history"
    r.rpush(key, json.dumps(round_obj, ensure_ascii=False))


def history_len(user_id: str) -> int:
    return get_redis().llen(f"session:{user_id}:history")


def fetch_unsummarized_tail(user_id: str, k: int = 6) -> List[Dict]:
    r = get_redis()
    cursor = int(r.get(f"session:{user_id}:summary:rounds") or 0)
    items = r.lrange(f"session:{user_id}:history", cursor, -1)
    return [json.loads(x) for x in items[-k:]]


def fetch_all_history(user_id: str) -> List[Dict]:
    r = get_redis()
    items = r.lrange(f"session:{user_id}:history", 0, -1)
    return [json.loads(x) for x in items]


def get_summary(user_id: str) -> Tuple[str, int]:
    r = get_redis()
    text = r.get(f"session:{user_id}:summary:text") or ""
    rounds = int(r.get(f"session:{user_id}:summary:rounds") or 0)
    return text, rounds


def peek_next_n(user_id: str, n: int) -> Tuple[Optional[int], List[Dict]]:
    r = get_redis()
    cursor = int(r.get(f"session:{user_id}:summary:rounds") or 0)
    total = r.llen(f"session:{user_id}:history")
    if (total - cursor) < n:
        return None, []
    items = r.lrange(f"session:{user_id}:history", cursor, cursor + n - 1)
    return cursor, [json.loads(x) for x in items]


def peek_remaining(user_id: str) -> Tuple[int, List[Dict]]:
    r = get_redis()
    cursor = int(r.get(f"session:{user_id}:summary:rounds") or 0)
    total = r.llen(f"session:{user_id}:history")
    if total <= cursor:
        return cursor, []
    items = r.lrange(f"session:{user_id}:history", cursor, total - 1)
    return cursor, [json.loads(x) for x in items]


def commit_summary_chunk(user_id: str, expected_cursor: int, advance: int, add_text: str) -> bool:
    r = get_redis()
    ckey = f"session:{user_id}:summary:rounds"
    tkey = f"session:{user_id}:summary:text"
    with r.pipeline() as p:
        while True:
            try:
                p.watch(ckey, tkey)
                cur = int(p.get(ckey) or 0)
                if cur != expected_cursor:
                    p.unwatch()
                    return False
                old = p.get(tkey) or ""
                new = (old + ("\n\n" if old else "") + (add_text or "").strip()) if add_text else old
                p.multi()
                p.set(tkey, new)
                p.set(ckey, cur + int(advance))
                p.execute()
                return True
            except redis.WatchError:
                return False

def set_state_if(user_id: str, expect: str, to: str) -> bool:
    r = get_redis()
    key = f"session:{user_id}:state"
    try:
        with r.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    cur = pipe.get(key)
                    if expect is None or expect == "":
                        if cur not in (None, ""):
                            pipe.unwatch()
                            return False
                    else:
                        if cur != expect:
                            pipe.unwatch()
                            return False
                    pipe.multi()
                    pipe.set(key, to)
                    pipe.execute()
                    return True
                except redis.WatchError:
                    return False
    except Exception:
        return False


def append_audio_segment(
    user_id: str, audio_id: str, seg: str, ttl_sec: int = 3600
) -> None:
    r = get_redis()
    key = f"audio:{user_id}:{audio_id}:buf"
    r.rpush(key, seg)
    r.expire(key, ttl_sec)


def read_and_clear_audio_segments(user_id: str, audio_id: str) -> str:
    r = get_redis()
    key = f"audio:{user_id}:{audio_id}:buf"
    with r.pipeline() as p:
        p.lrange(key, 0, -1)
        p.delete(key)
        parts, _ = p.execute()
    try:
        parts = [
            x if isinstance(x, str) else x.decode("utf-8", "ignore") for x in parts
        ]
    except Exception:
        parts = []
    return " ".join([p.strip() for p in parts if p])


def get_audio_result(user_id: str, audio_id: str) -> Optional[str]:
    return get_redis().get(f"audio:{user_id}:{audio_id}:result")


def set_audio_result(
    user_id: str, audio_id: str, reply: str, ttl_sec: int = 86400
) -> None:
    get_redis().set(f"audio:{user_id}:{audio_id}:result", reply, ex=ttl_sec)


# ---- Lightweight audio locks (separate from session state) ----
def acquire_audio_lock(lock_id: str, ttl_sec: int = 60) -> bool:
    """Try acquire a short-lived lock; return True on success.

    Use a dedicated key independent from session state to avoid interference.
    """
    r = get_redis()
    key = f"lock:audio:{lock_id}"
    try:
        # SET NX with expiration
        return bool(r.set(key, "1", nx=True, ex=ttl_sec))
    except Exception:
        return False


def release_audio_lock(lock_id: str) -> None:
    r = get_redis()
    key = f"lock:audio:{lock_id}"
    try:
        r.delete(key)
    except Exception:
        pass

