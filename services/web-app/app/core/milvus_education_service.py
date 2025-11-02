# services/web-app/app/core/milvus_education_service.py
"""
Milvus service for education content management
管理衛教資源的向量資料庫操作
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pymilvus import Collection, connections, utility, MilvusException
from app.core.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

class MilvusEducationService:
    def __init__(self):
        self.collection_name = "copd_qa"
        self.embedding_service = get_embedding_service()
        self.collection = None
        self._connect()
    
    def _connect(self):
        """連接到 Milvus 資料庫"""
        try:
            # 從環境變數讀取 URI
            uri = os.getenv("MILVUS_URI", "http://localhost:19530")
            
            # 嘗試連接
            connections.connect(alias="default", uri=uri)
            
            # 檢查 collection 是否存在
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.info(f"Successfully connected to Milvus collection: {self.collection_name}")
            else:
                logger.warning(f"Collection {self.collection_name} does not exist. Please run load_article.py first.")
                
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            # 如果是 Docker 環境，嘗試使用 milvus:19530
            if "localhost" in uri:
                try:
                    docker_uri = "http://milvus:19530"
                    connections.connect(alias="default", uri=docker_uri)
                    if utility.has_collection(self.collection_name):
                        self.collection = Collection(self.collection_name)
                        self.collection.load()
                        logger.info(f"Connected to Milvus via Docker network: {docker_uri}")
                except Exception as docker_e:
                    logger.error(f"Also failed to connect via Docker network: {docker_e}")
                    raise
    
    # 註：Web-App 不需要向量搜尋功能，只做 CRUD
    # 向量搜尋功能保留在 ai-worker 中供 RAG 使用
    
    def get_all(self, category: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        取得所有資料（支援類別篩選）
        
        Args:
            category: 篩選的類別（可選）
            limit: 返回結果數量上限
            
        Returns:
            問答資料列表
        """
        if not self.collection:
            logger.error("Milvus collection not available")
            return []
        
        try:
            # 建立查詢表達式
            expr = f'category == "{category}"' if category else ""
            
            # 執行查詢
            results = self.collection.query(
                expr=expr,
                output_fields=["category", "question", "answer", "keywords", "notes"],
                limit=limit
            )
            
            # 加入 ID（Milvus 預設不返回主鍵）
            for i, result in enumerate(results):
                if "id" not in result:
                    result["id"] = f"edu_{i}"  # 臨時 ID
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting all education data: {e}")
            return []
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        新增問答
        
        Args:
            data: 包含 category, question, answer, keywords, notes 的字典
            
        Returns:
            成功訊息或錯誤
        """
        if not self.collection:
            raise ValueError("Milvus collection not available")
        
        try:
            # 生成向量
            combined_text = f"{data.get('question', '')} {data.get('answer', '')}"
            vector = self.embedding_service.to_vector(combined_text)
            
            if not vector:
                raise ValueError("Failed to generate embedding vector")
            
            # 準備插入資料
            entities = [
                [data.get("category", "")],        # category
                [data.get("question", "")],        # question
                [data.get("answer", "")],          # answer
                [data.get("keywords", "")],        # keywords
                [data.get("notes", "")],           # notes
                [vector]                           # embedding
            ]
            
            # 插入資料
            insert_result = self.collection.insert(entities)
            
            # 立即 flush 確保資料寫入
            self.collection.flush()
            
            # 返回結果
            inserted_id = insert_result.primary_keys[0]
            logger.info(f"Successfully created education item with ID: {inserted_id}")
            
            return {
                "success": True,
                "id": inserted_id,
                "message": "Education item created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating education item: {e}")
            raise
    
    def update(self, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新問答（Milvus 不支援直接更新，需要刪除後重建）
        
        Args:
            item_id: 要更新的項目 ID
            data: 更新的資料
            
        Returns:
            成功訊息或錯誤
        """
        if not self.collection:
            raise ValueError("Milvus collection not available")
        
        try:
            # 先取得原始資料（如果需要保留某些欄位）
            existing = self.collection.query(
                expr=f"id == {item_id}",
                output_fields=["category", "question", "answer", "keywords", "notes"],
                limit=1
            )
            
            if not existing:
                raise ValueError(f"Education item with ID {item_id} not found")
            
            # 合併新舊資料
            updated_data = {**existing[0], **data}
            
            # 刪除舊資料
            self.collection.delete(f"id == {item_id}")
            
            # 新增更新後的資料
            result = self.create(updated_data)
            
            logger.info(f"Successfully updated education item with ID: {item_id}")
            return {
                "success": True,
                "id": item_id,
                "message": "Education item updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating education item: {e}")
            raise
    
    def delete(self, item_id: int) -> Dict[str, Any]:
        """
        刪除問答
        
        Args:
            item_id: 要刪除的項目 ID
            
        Returns:
            成功訊息或錯誤
        """
        if not self.collection:
            raise ValueError("Milvus collection not available")
        
        try:
            # 刪除資料
            expr = f"id == {item_id}"
            self.collection.delete(expr)
            
            # 立即 flush 確保刪除生效
            self.collection.flush()
            
            logger.info(f"Successfully deleted education item with ID: {item_id}")
            return {
                "success": True,
                "message": f"Education item {item_id} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting education item: {e}")
            raise
    
    def get_categories(self) -> List[str]:
        """
        取得所有類別
        
        Returns:
            類別列表
        """
        if not self.collection:
            return []
        
        try:
            # 查詢所有不重複的類別
            all_items = self.collection.query(
                expr="",
                output_fields=["category"],
                limit=10000
            )
            
            # 提取不重複的類別
            categories = list(set(item.get("category", "") for item in all_items if item.get("category")))
            categories.sort()
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

# 單例模式
_milvus_service = None

def get_milvus_education_service():
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusEducationService()
    return _milvus_service
