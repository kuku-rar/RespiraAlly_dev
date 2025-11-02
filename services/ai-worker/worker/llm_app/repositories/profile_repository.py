# llm_app/repositories/profile_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.chat_profile import SessionLocal, ChatUserProfile
from datetime import datetime
import json

class ProfileRepository:
    def _get_db(self) -> Session:
        return SessionLocal()

    def get_or_create_by_user_id(self, user_id: int, line_user_id: str = None) -> ChatUserProfile:
        """讀取 Profile，若不存在則建立一筆新的空紀錄。"""
        db = self._get_db()
        try:
            profile = db.query(ChatUserProfile).filter(ChatUserProfile.user_id == user_id).first()
            if not profile:
                print(f"[Profile Repo] 找不到 user_id={user_id} 的 Profile，將建立新紀錄。")
            
                profile = ChatUserProfile(
                    user_id=user_id,
                    line_user_id=line_user_id,
                    last_contact_ts=func.now()
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
            return profile
        finally:
            db.close()

    def read_profile_as_dict(self, user_id: str) -> dict:
        """讀取 Profile 並以字典格式回傳。"""
        profile = self.get_or_create_by_user_id(user_id)
        return {
            "personal_background": profile.profile_personal_background or {},
            "health_status": profile.profile_health_status or {},
            "life_events": profile.profile_life_events or {}
        }

    def update_profile_facts(self, user_id: int, facts_to_update: dict) -> None:
        """根據 Profiler 產生的指令集，安全地更新 Profile。"""
        if not facts_to_update or (not facts_to_update.get('add') and not facts_to_update.get('update') and not facts_to_update.get('remove')):
            print(f"[Profile Repo] 無任何更新指令，跳過 {user_id} 的 Profile 更新。")
            return

        db = self._get_db()
        try:
            profile = db.query(ChatUserProfile).filter(ChatUserProfile.user_id == user_id).first()
            if not profile:
                print(f"[Profile Repo] 更新失敗，找不到 user_id={user_id} 的 Profile。")
                return

            is_modified = False

            # 深度合併字典
            def deep_merge(d1, d2):
                for k, v in d2.items():
                    if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                        d1[k] = deep_merge(d1[k], v)
                    else:
                        d1[k] = v
                return d1

            # 處理 'add' 和 'update'
            for op in ['add', 'update']:
                for category_key, facts in facts_to_update.get(op, {}).items():
                    # Profiler 的輸出是 personal_background, health_status...
                    field_name = f"profile_{category_key}"
                    if hasattr(profile, field_name):
                        current_data = getattr(profile, field_name) or {}
                        updated_data = deep_merge(dict(current_data), facts)
                        setattr(profile, field_name, updated_data)
                        is_modified = True

            # 處理 'remove'
            for key_to_remove in facts_to_update.get('remove', []):
                parts = key_to_remove.split('.')
                if not parts: continue
                category_key = parts[0]
                field_name = f"profile_{category_key}"
                if hasattr(profile, field_name):
                    current_data = getattr(profile, field_name)
                    if current_data and isinstance(current_data, dict):
                        # 創建副本以進行修改
                        temp_data_root = dict(current_data)
                        temp_data = temp_data_root
                        
                        # 遍歷路徑直到最後一個 key
                        parent = None
                        key_to_del = None
                        for i, part in enumerate(parts[1:]):
                            if i == len(parts) - 2: # 倒數第二個
                                parent = temp_data
                                key_to_del = part
                                break
                            if isinstance(temp_data, dict) and part in temp_data:
                                temp_data = temp_data[part]
                            else:
                                temp_data = None
                                break
                        
                        if parent is not None and key_to_del is not None and key_to_del in parent:
                            del parent[key_to_del]
                            setattr(profile, field_name, temp_data_root)
                            is_modified = True

            if is_modified:
                profile.updated_at = func.now()
                db.commit()
                print(f"✅ [Profile Repo] 成功更新 user {user_id} 的 Profile。")
            else:
                print(f"ℹ️ [Profile Repo] user {user_id} 的 Profile 無需變動。")
        except Exception as e:
            db.rollback()
            print(f"❌ [Profile Repo] 更新 user {user_id} 的 Profile 失敗: {e}", exc_info=True)
        finally:
            db.close()

    def touch_last_contact_ts(self, user_id: str, line_user_id: str = None) -> None:
        """更新最後聯絡時間"""
        db = self._get_db()
        try:
            profile = db.query(ChatUserProfile).filter(ChatUserProfile.user_id == int(user_id)).first()

            # 如果使用者不存在，理論上應該在之前的流程被建立，但此處做個保險
            if not profile:
                print(f"DEBUG: Profile for user {user_id} not found, creating it.")
                profile = ChatUserProfile(
                    user_id=int(user_id),
                    line_user_id=line_user_id,
                )
                db.add(profile)
            
            # 更新時間
            profile.last_contact_ts = func.now()
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"❌ [Profile Repo] 更新 user_id={user_id} 的 last_contact_ts 失敗: {e}")
        finally:
            db.close()