# services/web-app/app/core/embedding_service.py
"""
Embedding service for education content
複製自 ai-worker 的 embedding.py，供 web-app 直接使用
"""
import os
from openai import OpenAI
from typing import Union, List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, embedding service will not work")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
    
    def to_vector(self, text: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        """
        將文字轉換為向量表示
        
        Args:
            text: 單一字串或字串列表
            normalize: 是否正規化向量（目前未使用）
            
        Returns:
            單一向量或向量列表
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")
        
        if isinstance(text, str):
            inputs = [text]
        elif isinstance(text, list):
            inputs = text
        else:
            raise TypeError("輸入必須為 str 或 List[str]")
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=inputs
            )
            
            vectors = [r.embedding for r in response.data]
            
            if isinstance(text, str):
                return vectors[0]
            return vectors
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def safe_to_vector(self, text: Union[str, List[str]], normalize: bool = True):
        """
        安全版本的向量轉換，發生錯誤時返回空列表
        """
        try:
            return self.to_vector(text, normalize=normalize)
        except Exception as e:
            logger.error(f"[embedding error] {e}")
            return [] if isinstance(text, str) else [[] for _ in text]

# 單例模式
_embedding_service = None

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
